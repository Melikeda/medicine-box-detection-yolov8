from __future__ import annotations

import time
from pathlib import Path

import easyocr
from ultralytics import YOLO

from src.ocr.ocr_reader import create_ocr_reader
from src.ocr.ocr_pipeline import DEFAULT_BLUR_THRESHOLD
from src.services.candidate_processor import has_weak_ocr_candidates
from src.services.config import PipelineConfig
from src.services.detection_service import DetectionService
from src.services.matching_service import MatchingService, TextMatchResult
from src.services.medicine_analyzer import (
    BoxAnalysisResult,
    MedicineAnalysisResult,
    MultiMedicineAnalysisResult,
    PipelineTiming,
)
from src.services.ocr_service import OCRService

BOX_ERROR_MESSAGE = "Bu ilaç kutusu analiz edilemedi."


class PipelineManager:
    """
    Pipeline kaynaklarını startup'ta bir kez yükleyen singleton yönetici.

    FastAPI lifespan veya CLI script başlangıcında load() çağrılır;
    her analiz isteğinde modeller yeniden yüklenmez.
    """

    _instance: PipelineManager | None = None

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()
        self._yolo_model: YOLO | None = None
        self._ocr_reader: easyocr.Reader | None = None
        self._detection_service: DetectionService | None = None
        self._ocr_service: OCRService | None = None
        self._matching_service: MatchingService | None = None

    @classmethod
    def get_instance(
        cls,
        config: PipelineConfig | None = None,
    ) -> PipelineManager:
        """Singleton instance döndürür."""
        if cls._instance is None:
            cls._instance = cls(config)
        elif config is not None:
            cls._instance.config = config
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Test veya yeniden yapılandırma için singleton'ı sıfırlar."""
        cls._instance = None

    @property
    def is_loaded(self) -> bool:
        return self._yolo_model is not None

    @property
    def medicine_count(self) -> int | None:
        if self._matching_service is None:
            return None
        return self._matching_service.medicine_count

    @property
    def database_source(self) -> str | None:
        if self._matching_service is None:
            return None
        return self._matching_service.source

    def load(self) -> None:
        """YOLO, EasyOCR ve ilaç veritabanını belleğe yükler."""
        if self.is_loaded:
            print("PipelineManager: kaynaklar zaten yüklü.")
            return

        self._validate_paths()

        print("PipelineManager: YOLO modeli yükleniyor...")
        self._yolo_model = YOLO(str(self.config.model_path))

        print("PipelineManager: EasyOCR reader hazırlanıyor...")
        self._ocr_reader = create_ocr_reader(
            languages=list(self.config.ocr_languages),
            use_gpu=self.config.use_gpu,
        )

        print("PipelineManager: ilaç veritabanı yükleniyor...")
        self._matching_service = MatchingService.from_config(
            config=self.config,
        )

        self._detection_service = DetectionService(
            config=self.config,
            model=self._yolo_model,
        )
        self._ocr_service = OCRService(
            config=self.config,
            reader=self._ocr_reader,
        )

        print(
            f"PipelineManager: hazır "
            f"({self._matching_service.medicine_count} ilaç, "
            f"kaynak: {self._matching_service.source}, "
            f"OCR modu: {self.config.ocr_mode})"
        )

    def unload(self) -> None:
        """Yüklenen kaynakları serbest bırakır."""
        self._yolo_model = None
        self._ocr_reader = None
        self._detection_service = None
        self._ocr_service = None
        self._matching_service = None

    def analyze_all(
        self,
        image_path: str | Path,
        *,
        save_debug_outputs: bool = False,
    ) -> MultiMedicineAnalysisResult:
        """Fotoğraftaki tüm kutuları sırayla analiz eder."""
        if not self.is_loaded:
            self.load()

        assert self._detection_service is not None
        assert self._ocr_service is not None
        assert self._matching_service is not None

        image_path = Path(image_path)
        medicines_compared = self._matching_service.medicine_count
        timing = PipelineTiming()
        pipeline_started = time.perf_counter()

        if save_debug_outputs:
            self.config.output_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

        yolo_started = time.perf_counter()
        detected_boxes = self._detection_service.detect_all(
            image_path=image_path,
        )
        timing.yolo_ms = (time.perf_counter() - yolo_started) * 1000

        detection_count = len(detected_boxes)
        print(f"YOLO tespit sayısı: {detection_count}")

        if detection_count == 0:
            return MultiMedicineAnalysisResult(
                success=False,
                image_path=str(image_path),
                detection_count=0,
                medicines_compared=medicines_compared,
                error=(
                    "İlaç kutusu tespit edilemedi. "
                    "Fotoğrafın net olduğundan, kutuların kadrajda "
                    "ve yeterince büyük göründüğünden emin olun."
                ),
            )

        box_results: list[BoxAnalysisResult] = []

        for index, detected_box in enumerate(detected_boxes, start=1):
            print(f"\nKutu {index}/{detection_count}")
            print(
                f"YOLO confidence: {detected_box.confidence:.2f}"
            )

            try:
                ocr_started = time.perf_counter()
                candidate_texts, match_result, pipeline_result = (
                    self._analyze_detected_box(
                        detected_box=detected_box,
                        box_index=index,
                        save_debug_outputs=save_debug_outputs,
                    )
                )
                timing.ocr_ms += (
                    time.perf_counter() - ocr_started
                ) * 1000

                ocr_text = match_result.best_ocr_text
                if ocr_text:
                    print(f"OCR metni: {ocr_text}")

                if match_result.status == "matched":
                    print(f"Sonuç: {match_result.medicine_name}")
                    print(
                        f"Eşleşme skoru: {match_result.matching_score:.2f}"
                    )
                elif match_result.status == "not_medicine_box":
                    print(f"Sonuç: {match_result.display_message}")
                else:
                    print("Sonuç: CSV veritabanında bulunamadı")
                    if match_result.best_candidate:
                        print(
                            "En yakın aday: "
                            f"{match_result.best_candidate} "
                            f"({match_result.matching_score:.2f})"
                        )

                box_results.append(
                    BoxAnalysisResult(
                        box_index=index,
                        bounding_box=detected_box.bounding_box,
                        yolo_confidence=detected_box.confidence,
                        ocr_text=ocr_text,
                        medicine_name=match_result.medicine_name,
                        matching_score=match_result.matching_score,
                        status=match_result.status,
                        display_message=match_result.display_message,
                        best_candidate=match_result.best_candidate,
                        medicine=match_result.medicine,
                    )
                )

            except Exception as exc:
                print(f"Hata: {exc}")
                box_results.append(
                    BoxAnalysisResult(
                        box_index=index,
                        bounding_box=detected_box.bounding_box,
                        yolo_confidence=detected_box.confidence,
                        status="error",
                        display_message=BOX_ERROR_MESSAGE,
                        error=str(exc),
                    )
                )

        has_matched_box = any(
            box.status == "matched" for box in box_results
        )
        has_valid_detection = any(
            box.status in {"matched", "not_found"}
            for box in box_results
        )

        timing.total_ms = (
            time.perf_counter() - pipeline_started
        ) * 1000

        return MultiMedicineAnalysisResult(
            success=has_matched_box or has_valid_detection,
            image_path=str(image_path),
            detection_count=detection_count,
            medicines=box_results,
            medicines_compared=medicines_compared,
            timing=timing,
        )

    def analyze(
        self,
        image_path: str | Path,
        *,
        save_debug_outputs: bool = False,
    ) -> MedicineAnalysisResult:
        """Tek kutulu analiz (geriye dönük uyumluluk)."""
        multi_result = self.analyze_all(
            image_path=image_path,
            save_debug_outputs=save_debug_outputs,
        )

        if multi_result.detection_count == 0:
            return MedicineAnalysisResult(
                success=False,
                medicines_compared=multi_result.medicines_compared,
                error=multi_result.error,
            )

        first_box = multi_result.medicines[0]

        if first_box.status == "error":
            return MedicineAnalysisResult(
                success=False,
                yolo_confidence=first_box.yolo_confidence,
                medicines_compared=multi_result.medicines_compared,
                error=first_box.error,
            )

        if first_box.status == "matched" and first_box.medicine:
            return MedicineAnalysisResult(
                success=True,
                yolo_confidence=first_box.yolo_confidence,
                medicine=first_box.medicine,
                match_score=first_box.matching_score,
                best_ocr_text=first_box.ocr_text,
                ranked_matches=[],
                medicines_compared=multi_result.medicines_compared,
            )

        return MedicineAnalysisResult(
            success=False,
            yolo_confidence=first_box.yolo_confidence,
            match_score=first_box.matching_score,
            best_ocr_text=first_box.ocr_text,
            medicines_compared=multi_result.medicines_compared,
            error=first_box.display_message,
        )

    def _analyze_detected_box(
        self,
        *,
        detected_box,
        box_index: int,
        save_debug_outputs: bool,
    ) -> tuple[list[str], TextMatchResult, object]:
        """OCR + eslestirme; zayif sonucta ek acilarla tekrar dener."""
        assert self._ocr_service is not None
        assert self._matching_service is not None

        early_stop = (
            self._build_early_stop_checker()
            if self.config.ocr_early_exit
            else None
        )
        candidate_texts, pipeline_result = (
            self._ocr_service.analyze_crop(
                cropped_image=detected_box.cropped_image,
                box_index=box_index,
                save_debug_outputs=save_debug_outputs,
                debug_subdirectory=f"box_{box_index:02d}",
                should_stop_after_variant=early_stop,
            )
        )
        match_result = self._matching_service.match_text(
            candidate_texts=candidate_texts,
        )

        if self._should_retry_ocr(match_result):
            retry_angles = self.config.ocr_retry_rotation_angles
            if retry_angles:
                print(
                    f"OCR tekrar deneniyor "
                    f"(kutu {box_index}, acilar: {retry_angles})"
                )
                retry_texts, retry_pipeline_result = (
                    self._ocr_service.analyze_crop(
                        cropped_image=detected_box.cropped_image,
                        box_index=box_index,
                        save_debug_outputs=save_debug_outputs,
                        debug_subdirectory=(
                            f"box_{box_index:02d}_retry"
                        ),
                        should_stop_after_variant=None,
                        rotation_angles=retry_angles,
                    )
                )
                candidate_texts = list(
                    dict.fromkeys(candidate_texts + retry_texts)
                )
                match_result = self._matching_service.match_text(
                    candidate_texts=candidate_texts,
                )
                pipeline_result = retry_pipeline_result

        if self._should_supplemental_ocr(match_result, candidate_texts):
            print(
                f"OCR derin tekrar (kutu {box_index}): "
                "2x olcek, gelismis preprocessing"
            )
            supplemental_texts, supplemental_pipeline_result = (
                self._ocr_service.analyze_crop(
                    cropped_image=detected_box.cropped_image,
                    box_index=box_index,
                    save_debug_outputs=save_debug_outputs,
                    debug_subdirectory=(
                        f"box_{box_index:02d}_deep"
                    ),
                    should_stop_after_variant=None,
                    rotation_angles=(0, 90, 180, 270),
                    scale_factor=self.config.ocr_scale_factor_accurate,
                    limited_variants=False,
                    blur_threshold=DEFAULT_BLUR_THRESHOLD,
                )
            )
            candidate_texts = list(
                dict.fromkeys(candidate_texts + supplemental_texts)
            )
            match_result = self._matching_service.match_text(
                candidate_texts=candidate_texts,
            )
            pipeline_result = supplemental_pipeline_result

        return candidate_texts, match_result, pipeline_result

    def _should_supplemental_ocr(
        self,
        match_result: TextMatchResult,
        candidate_texts: list[str],
    ) -> bool:
        if match_result.status == "matched":
            return False

        if has_weak_ocr_candidates(candidate_texts):
            return True

        return match_result.status in {
            "not_found",
            "not_medicine_box",
        }

    def _should_retry_ocr(
        self,
        match_result: TextMatchResult,
    ) -> bool:
        if not self.config.ocr_retry_rotation_angles:
            return False

        return match_result.status in {
            "not_found",
            "not_medicine_box",
        }

    def _build_early_stop_checker(self):
        """Güvenilir eşleşme bulunduğunda OCR varyant döngüsünü durdurur."""
        assert self._matching_service is not None
        minimum_score = self.config.minimum_match_score

        def should_stop(candidate_texts: list[str]) -> bool:
            if not candidate_texts:
                return False
            match_result = self._matching_service.match_text(
                candidate_texts=candidate_texts,
            )
            return (
                match_result.status == "matched"
                and match_result.matching_score >= minimum_score
            )

        return should_stop

    def _validate_paths(self) -> None:
        required_paths = {
            "YOLO modeli": self.config.model_path,
            "İlaç CSV dosyası": self.config.medicines_csv_path,
        }

        for path_name, path in required_paths.items():
            if not path.exists():
                raise FileNotFoundError(
                    f"{path_name} bulunamadı: {path}"
                )

            if not path.is_file():
                raise ValueError(
                    f"{path_name} bir dosya değil: {path}"
                )
