from __future__ import annotations

from pathlib import Path

import easyocr
from ultralytics import YOLO

from src.ocr.ocr_reader import create_ocr_reader
from src.services.config import PipelineConfig
from src.services.detection_service import DetectionService
from src.services.matching_service import MatchingService
from src.services.medicine_analyzer import (
    MedicineAnalysisResult,
    build_analysis_result,
)
from src.services.ocr_service import OCRService


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

    def load(self) -> None:
        """YOLO, EasyOCR ve CSV veritabanını belleğe yükler."""
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
        self._matching_service = MatchingService.from_csv(
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
            f"OCR modu: {self.config.ocr_mode})"
        )

    def unload(self) -> None:
        """Yüklenen kaynakları serbest bırakır."""
        self._yolo_model = None
        self._ocr_reader = None
        self._detection_service = None
        self._ocr_service = None
        self._matching_service = None

    def analyze(
        self,
        image_path: str | Path,
        *,
        save_debug_outputs: bool = False,
    ) -> MedicineAnalysisResult:
        """Yüklü servislerle tam pipeline analizini çalıştırır."""
        if not self.is_loaded:
            self.load()

        assert self._detection_service is not None
        assert self._ocr_service is not None
        assert self._matching_service is not None

        image_path = Path(image_path)
        medicines_compared = self._matching_service.medicine_count

        if save_debug_outputs:
            self.config.output_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

        crop_result = self._detection_service.detect_and_crop(
            image_path=image_path,
        )

        if crop_result is None:
            return MedicineAnalysisResult(
                success=False,
                medicines_compared=medicines_compared,
                error=(
                    "İlaç kutusu tespit edilemedi "
                    "veya crop oluşturulamadı."
                ),
            )

        cropped_image, yolo_confidence = crop_result

        candidate_texts, _ = self._ocr_service.extract_candidates(
            cropped_image=cropped_image,
            save_debug_outputs=save_debug_outputs,
        )

        expanded_candidates, filtered_candidates = (
            self._matching_service.process_candidates(
                candidate_texts=candidate_texts,
            )
        )

        if not filtered_candidates:
            return MedicineAnalysisResult(
                success=False,
                yolo_confidence=yolo_confidence,
                ocr_candidates=candidate_texts,
                expanded_candidates=expanded_candidates,
                filtered_candidates=filtered_candidates,
                medicines_compared=medicines_compared,
                error="Eşleştirmeye uygun OCR adayı bulunamadı.",
            )

        ranked_matches = self._matching_service.rank_matches(
            filtered_candidates=filtered_candidates,
        )

        return build_analysis_result(
            config=self.config,
            yolo_confidence=yolo_confidence,
            candidate_texts=candidate_texts,
            expanded_candidates=expanded_candidates,
            filtered_candidates=filtered_candidates,
            ranked_matches=ranked_matches,
            medicines_compared=medicines_compared,
        )

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
