from dataclasses import dataclass, field
from pathlib import Path

import easyocr
from ultralytics import YOLO

from src.database.csv_reader import load_medicines
from src.ocr.ocr_pipeline import (
    get_candidate_texts,
    run_ocr_pipeline,
)
from src.ocr.ocr_reader import create_ocr_reader
from src.services.candidate_processor import (
    MatchRecord,
    create_medicine_name_candidates,
    filter_candidate_texts,
    rank_medicine_matches,
)
from src.services.config import PipelineConfig
from src.services.detection import crop_best_detection


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


def _validate_config(config: PipelineConfig) -> None:
    """Gerekli dosya yollarının varlığını kontrol eder."""
    required_paths = {
        "YOLO modeli": config.model_path,
        "İlaç CSV dosyası": config.medicines_csv_path,
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


def analyze_medicine_box(
    image_path: str | Path,
    *,
    config: PipelineConfig | None = None,
    reader: easyocr.Reader | None = None,
    model: YOLO | None = None,
    save_debug_outputs: bool = False,
) -> MedicineAnalysisResult:
    """
    Görüntüden ilaç kutusunu tespit eder, OCR ve RapidFuzz ile eşleştirir.

    İşlem sırası:
    1. YOLO ile ilaç kutusunu tespit et
    2. En güvenilir bounding box'ı kırp
    3. Çoklu preprocessing ve OCR çalıştır
    4. OCR adaylarından tam ilaç adı adayları üret
    5. Adayları filtrele
    6. RapidFuzz ile veritabanından eşleştir
    """
    config = config or PipelineConfig()
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Görüntü bulunamadı: {image_path}"
        )

    if not image_path.is_file():
        raise ValueError(
            f"Görüntü yolu bir dosya değil: {image_path}"
        )

    _validate_config(config)

    medicines = load_medicines(
        csv_path=config.medicines_csv_path,
    )

    yolo_model = model or YOLO(str(config.model_path))

    prediction_results = yolo_model.predict(
        source=str(image_path),
        conf=config.confidence_threshold,
        save=False,
        verbose=False,
    )

    if not prediction_results:
        return MedicineAnalysisResult(
            success=False,
            medicines_compared=len(medicines),
            error="YOLO tahmin sonucu alınamadı.",
        )

    crop_result = crop_best_detection(
        result=prediction_results[0],
    )

    if crop_result is None:
        return MedicineAnalysisResult(
            success=False,
            medicines_compared=len(medicines),
            error=(
                "İlaç kutusu tespit edilemedi "
                "veya crop oluşturulamadı."
            ),
        )

    cropped_image, yolo_confidence = crop_result

    ocr_reader = reader or create_ocr_reader(
        languages=list(config.ocr_languages),
        use_gpu=config.use_gpu,
    )

    if save_debug_outputs:
        config.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    pipeline_result = run_ocr_pipeline(
        reader=ocr_reader,
        image_input=cropped_image,
        scale_factor=config.ocr_scale_factor,
        minimum_confidence=config.minimum_ocr_confidence,
        save_preprocessed_images=save_debug_outputs,
        output_directory=(
            config.ocr_variants_directory
            if save_debug_outputs
            else None
        ),
    )

    candidate_texts = get_candidate_texts(
        pipeline_result=pipeline_result,
    )

    expanded_candidate_texts = create_medicine_name_candidates(
        candidate_texts=candidate_texts,
    )

    filtered_candidate_texts = filter_candidate_texts(
        candidate_texts=expanded_candidate_texts,
    )

    if not filtered_candidate_texts:
        return MedicineAnalysisResult(
            success=False,
            yolo_confidence=yolo_confidence,
            ocr_candidates=candidate_texts,
            expanded_candidates=expanded_candidate_texts,
            filtered_candidates=filtered_candidate_texts,
            medicines_compared=len(medicines),
            error="Eşleştirmeye uygun OCR adayı bulunamadı.",
        )

    ranked_matches = rank_medicine_matches(
        candidate_texts=filtered_candidate_texts,
        medicines=medicines,
        top_count=config.top_match_count,
    )

    if not ranked_matches:
        return MedicineAnalysisResult(
            success=False,
            yolo_confidence=yolo_confidence,
            ocr_candidates=candidate_texts,
            expanded_candidates=expanded_candidate_texts,
            filtered_candidates=filtered_candidate_texts,
            ranked_matches=ranked_matches,
            medicines_compared=len(medicines),
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
            expanded_candidates=expanded_candidate_texts,
            filtered_candidates=filtered_candidate_texts,
            medicines_compared=len(medicines),
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
        expanded_candidates=expanded_candidate_texts,
        filtered_candidates=filtered_candidate_texts,
        medicines_compared=len(medicines),
    )
