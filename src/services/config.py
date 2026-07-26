from dataclasses import dataclass, field
from pathlib import Path


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
    match_score_cutoff: float = 80.0
    top_match_count: int = 3
    ocr_languages: tuple[str, ...] = ("tr", "en")
    use_gpu: bool = False

    @property
    def ocr_variants_directory(self) -> Path:
        return self.output_directory / "ocr_variants"
