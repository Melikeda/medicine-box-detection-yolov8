from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from src.services.candidate_processor import MatchRecord
from src.services.config import PipelineConfig

if TYPE_CHECKING:
    from src.services.pipeline_manager import PipelineManager


@dataclass
class MedicineAnalysisResult:
    """
    analyze_medicine_box() çıktısı.

    FastAPI ve mobil istemci bu yapıyı JSON'a dönüştürebilir.
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

    if best_score < config.match_score_cutoff:
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
                f"eşik: {config.match_score_cutoff:.2f})."
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


def analyze_medicine_box(
    image_path: str | Path,
    *,
    config: PipelineConfig | None = None,
    manager: PipelineManager | None = None,
    save_debug_outputs: bool = False,
) -> MedicineAnalysisResult:
    """
    Görüntüden ilaç kutusunu tespit eder, OCR ve RapidFuzz ile eşleştirir.

    Modeller PipelineManager singleton üzerinden bir kez yüklenir.
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

    return pipeline_manager.analyze(
        image_path=image_path,
        save_debug_outputs=save_debug_outputs,
    )
