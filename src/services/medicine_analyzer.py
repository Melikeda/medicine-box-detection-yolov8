from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from src.services.candidate_processor import MatchRecord
from src.services.config import PipelineConfig
from src.services.detection import BoundingBox

if TYPE_CHECKING:
    from src.services.pipeline_manager import PipelineManager

BOX_ERROR_MESSAGE = "Bu ilaç kutusu analiz edilemedi."


@dataclass
class MedicineAnalysisResult:
    """
    analyze_medicine_box() çıktısı — tek kutu (geriye dönük uyumluluk).
    """

    success: bool
    yolo_confidence: float | None = None
    medicine: dict[str, str] | None = None
    match_score: float = 0.0
    best_ocr_text: str | None = None
    ranked_matches: list[MatchRecord] = field(
        default_factory=list
    )
    ocr_candidates: list[str] = field(
        default_factory=list
    )
    expanded_candidates: list[str] = field(
        default_factory=list
    )
    filtered_candidates: list[str] = field(
        default_factory=list
    )
    medicines_compared: int = 0
    error: str | None = None


@dataclass
class PipelineTiming:
    """Analyze pipeline aşama süreleri (ms)."""

    yolo_ms: float = 0.0
    ocr_ms: float = 0.0
    matching_ms: float = 0.0
    total_ms: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass
class BoxAnalysisResult:
    """Tek bir ilaç kutusu için analiz sonucu."""

    box_index: int
    bounding_box: BoundingBox
    yolo_confidence: float
    ocr_text: str | None = None
    medicine_name: str | None = None
    matching_score: float = 0.0
    status: str = "not_found"
    display_message: str = ""
    best_candidate: str | None = None
    error: str | None = None
    medicine: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["bounding_box"] = self.bounding_box.to_dict()
        return data


@dataclass
class MultiMedicineAnalysisResult:
    """Fotoğraftaki tüm ilaç kutuları için analiz sonucu."""

    success: bool
    image_path: str
    detection_count: int
    medicines: list[BoxAnalysisResult] = field(default_factory=list)
    medicines_compared: int = 0
    error: str | None = None
    timing: PipelineTiming | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "image_path": self.image_path,
            "detection_count": self.detection_count,
            "medicines": [
                box_result.to_dict()
                for box_result in self.medicines
            ],
            "medicines_compared": self.medicines_compared,
            "error": self.error,
            "timing": self.timing.to_dict() if self.timing else None,
        }


def build_analysis_result(
    *,
    config: PipelineConfig,
    yolo_confidence: float,
    candidate_texts: list[str],
    expanded_candidates: list[str],
    filtered_candidates: list[str],
    ranked_matches: list[MatchRecord],
    medicines_compared: int,
) -> MedicineAnalysisResult:
    """Eşleştirme sonuçlarından MedicineAnalysisResult oluşturur."""
    if not ranked_matches:
        return MedicineAnalysisResult(
            success=False,
            yolo_confidence=yolo_confidence,
            ocr_candidates=candidate_texts,
            expanded_candidates=expanded_candidates,
            filtered_candidates=filtered_candidates,
            ranked_matches=ranked_matches,
            medicines_compared=medicines_compared,
            error="İlaç eşleşmesi bulunamadı.",
        )

    best_medicine, best_score, best_ocr_text = ranked_matches[0]

    if best_score < config.minimum_match_score:
        return MedicineAnalysisResult(
            success=False,
            yolo_confidence=yolo_confidence,
            medicine=best_medicine,
            match_score=best_score,
            best_ocr_text=best_ocr_text,
            ranked_matches=ranked_matches,
            ocr_candidates=candidate_texts,
            expanded_candidates=expanded_candidates,
            filtered_candidates=filtered_candidates,
            medicines_compared=medicines_compared,
            error=(
                f"Güvenilir eşleşme bulunamadı "
                f"(skor: {best_score:.2f}, "
                f"eşik: {config.minimum_match_score:.2f})."
            ),
        )

    return MedicineAnalysisResult(
        success=True,
        yolo_confidence=yolo_confidence,
        medicine=best_medicine,
        match_score=best_score,
        best_ocr_text=best_ocr_text,
        ranked_matches=ranked_matches,
        ocr_candidates=candidate_texts,
        expanded_candidates=expanded_candidates,
        filtered_candidates=filtered_candidates,
        medicines_compared=medicines_compared,
    )


def _box_result_to_single_result(
    box_result: BoxAnalysisResult,
    *,
    medicines_compared: int,
    ocr_candidates: list[str] | None = None,
) -> MedicineAnalysisResult:
    """Tek kutu sonucunu MedicineAnalysisResult'a dönüştürür."""
    if box_result.status == "error":
        return MedicineAnalysisResult(
            success=False,
            yolo_confidence=box_result.yolo_confidence,
            medicines_compared=medicines_compared,
            error=box_result.error,
        )

    if box_result.status == "matched" and box_result.medicine:
        return MedicineAnalysisResult(
            success=True,
            yolo_confidence=box_result.yolo_confidence,
            medicine=box_result.medicine,
            match_score=box_result.matching_score,
            best_ocr_text=box_result.ocr_text,
            ocr_candidates=ocr_candidates or [],
            medicines_compared=medicines_compared,
        )

    return MedicineAnalysisResult(
        success=False,
        yolo_confidence=box_result.yolo_confidence,
        medicine=box_result.medicine,
        match_score=box_result.matching_score,
        best_ocr_text=box_result.ocr_text,
        ocr_candidates=ocr_candidates or [],
        medicines_compared=medicines_compared,
        error=box_result.display_message,
    )


def analyze_medicine_boxes(
    image_path: str | Path,
    *,
    config: PipelineConfig | None = None,
    manager: PipelineManager | None = None,
    save_debug_outputs: bool = False,
) -> MultiMedicineAnalysisResult:
    """
    Fotoğraftaki tüm ilaç kutularını tespit eder, OCR ve eşleştirme yapar.

    FastAPI aşamasında kullanılacak ana fonksiyondur.
    """
    from src.services.pipeline_manager import PipelineManager

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Görüntü bulunamadı: {image_path}"
        )

    if not image_path.is_file():
        raise ValueError(
            f"Görüntü yolu bir dosya değil: {image_path}"
        )

    pipeline_manager = manager or PipelineManager.get_instance(
        config
    )

    if config is not None:
        pipeline_manager.config = config

    return pipeline_manager.analyze_all(
        image_path=image_path,
        save_debug_outputs=save_debug_outputs,
    )


def analyze_medicine_box(
    image_path: str | Path,
    *,
    config: PipelineConfig | None = None,
    manager: PipelineManager | None = None,
    save_debug_outputs: bool = False,
) -> MedicineAnalysisResult:
    """
    Tek kutulu analiz — en yüksek confidence'lı kutuyu işler.

    Geriye dönük uyumluluk için korunmuştur.
    """
    multi_result = analyze_medicine_boxes(
        image_path=image_path,
        config=config,
        manager=manager,
        save_debug_outputs=save_debug_outputs,
    )

    if multi_result.detection_count == 0:
        return MedicineAnalysisResult(
            success=False,
            medicines_compared=multi_result.medicines_compared,
            error=multi_result.error,
        )

    first_box = multi_result.medicines[0]
    return _box_result_to_single_result(
        first_box,
        medicines_compared=multi_result.medicines_compared,
    )
