"""YOLO weight path resolution (local train layouts + Docker defaults)."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Preferred when present: historical Ultralytics nested run used by Docker/compose.
LEGACY_NESTED_WEIGHTS = (
    PROJECT_ROOT
    / "runs"
    / "detect"
    / "runs"
    / "detect"
    / "medicine_box_yolov8n-2"
    / "weights"
    / "best.pt"
)

# Output of ``python src/train.py`` (project=runs/detect, name=medicine_box_yolov8n).
TRAIN_SCRIPT_WEIGHTS = (
    PROJECT_ROOT
    / "runs"
    / "detect"
    / "medicine_box_yolov8n"
    / "weights"
    / "best.pt"
)

# Optional manual drop location (see models/README.md).
MODELS_DIR_WEIGHTS = PROJECT_ROOT / "models" / "best.pt"


def candidate_model_paths(project_root: Path | None = None) -> tuple[Path, ...]:
    """Ordered weight candidates (first existing file wins)."""
    root = Path(project_root) if project_root is not None else PROJECT_ROOT
    return (
        root
        / "runs/detect/runs/detect/medicine_box_yolov8n-2/weights/best.pt",
        root / "runs/detect/medicine_box_yolov8n/weights/best.pt",
        root / "runs/detect/medicine_box_yolov8n-2/weights/best.pt",
        root / "models/best.pt",
    )


def resolve_default_model_path(project_root: Path | None = None) -> Path:
    """
    Return the first existing weight file, else the primary documented path.

    Does not raise — callers validate existence when loading the model.
    """
    candidates = candidate_model_paths(project_root)
    for path in candidates:
        if path.is_file():
            return path.resolve()
    return candidates[0]


def missing_model_help(missing_path: Path | None = None) -> str:
    """Human-readable hint when weights are absent."""
    path = missing_path or resolve_default_model_path()
    lines = [
        f"YOLO weights not found at: {path}",
        "Tried (in order):",
    ]
    for candidate in candidate_model_paths():
        mark = "exists" if candidate.is_file() else "missing"
        lines.append(f"  - [{mark}] {candidate}")
    lines.extend(
        [
            "",
            "Fix options:",
            "  1) Train: python src/train.py",
            "     → runs/detect/medicine_box_yolov8n/weights/best.pt",
            "  2) Copy your best.pt to models/best.pt",
            "  3) Set YOLO_MODEL_PATH to an absolute/relative weight file",
            "  4) Docker: mount weights via YOLO_MODEL_HOST_PATH "
            "(see docker-compose.yml)",
        ]
    )
    return "\n".join(lines)
