from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from src.ocr.ocr_pipeline import DEFAULT_BLUR_THRESHOLD

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MODEL_PATH = (
    PROJECT_ROOT
    / "runs/detect/runs/detect/"
    / "medicine_box_yolov8n-2/weights/best.pt"
)

DEFAULT_MEDICINES_CSV_PATH = (
    PROJECT_ROOT / "data/database/medicines.csv"
)

DEFAULT_OUTPUT_DIRECTORY = (
    PROJECT_ROOT / "results/integration/medicine_matching"
)

OCRMode = Literal["fast", "accurate"]

IGNORED_OCR_PHRASES = frozenset(
    {
        "film kaplı tablet",
        "film kapli tablet",
        "kaplı tablet",
        "kapli tablet",
        "tablet",
        "parasetamol",
        "klorfeniramin maleat",
    }
)

MEDICINE_NAME_SUFFIXES = frozenset(
    {
        "fort",
        "forte",
        "plus",
        "extra",
        "cold",
        "flu",
    }
)


@dataclass
class PipelineConfig:
    """
    Merkezi pipeline yapılandırması.

    Model yolları, eşik değerleri ve OCR ayarları
    tek noktadan yönetilir.
    """

    model_path: Path = field(
        default_factory=lambda: DEFAULT_MODEL_PATH
    )
    medicines_csv_path: Path = field(
        default_factory=lambda: DEFAULT_MEDICINES_CSV_PATH
    )
    output_directory: Path = field(
        default_factory=lambda: DEFAULT_OUTPUT_DIRECTORY
    )
    confidence_threshold: float = 0.60
    ocr_scale_factor: float = 2.0
    minimum_ocr_confidence: float = 0.0
    minimum_matching_text_length: int = 3
    minimum_name_coverage_ratio: float = 0.45
    minimum_match_score: float = 80.0
    top_match_count: int = 5
    ocr_languages: tuple[str, ...] = ("tr", "en")
    use_gpu: bool = False
    ocr_mode: OCRMode = "fast"

    @property
    def match_score_cutoff(self) -> float:
        """Geriye dönük uyumluluk alias'ı."""
        return self.minimum_match_score

    @property
    def ocr_variants_directory(self) -> Path:
        return self.output_directory / "ocr_variants"

    @property
    def ocr_rotation_angles(self) -> tuple[int, ...]:
        """Tüm modlarda dört açı; fast modda varyant sayısı sınırlıdır."""
        return (0, 90, 180, 270)

    @property
    def ocr_limited_variants(self) -> bool:
        """fast: açı başına 2 varyant | accurate: tam varyant seti."""
        return self.ocr_mode == "fast"

    @property
    def ocr_blur_threshold(self) -> float:
        """
        fast modda bulanık ek varyantları devre dışı bırakır.

        blur_score >= threshold olduğunda yalnızca standart
        preprocessing varyantları kullanılır.
        """
        if self.ocr_mode == "fast":
            return 0.0
        return DEFAULT_BLUR_THRESHOLD
