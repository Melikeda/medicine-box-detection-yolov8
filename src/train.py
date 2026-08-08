"""Train YOLOv8n on the local Roboflow export under data/dataset/."""

from pathlib import Path

from ultralytics import YOLO

# Must stay in sync with src/services/model_paths.TRAIN_SCRIPT_WEIGHTS
TRAIN_PROJECT = "runs/detect"
TRAIN_NAME = "medicine_box_yolov8n"


def train_model() -> None:
    dataset = Path("data/dataset/data.yaml")
    if not dataset.is_file():
        raise FileNotFoundError(
            f"Dataset config missing: {dataset}\n"
            "Download the Roboflow YOLO export into data/dataset/ "
            "(train/valid/test images are gitignored). "
            "See data/README.md and docs/reports/03-dataset-preparation.md."
        )

    # yolov8n.pt is downloaded by Ultralytics if missing locally.
    model = YOLO("yolov8n.pt")

    model.train(
        data=str(dataset),
        epochs=50,
        imgsz=640,
        batch=8,
        device="cpu",
        project=TRAIN_PROJECT,
        name=TRAIN_NAME,
    )

    weights = (
        Path(TRAIN_PROJECT) / TRAIN_NAME / "weights" / "best.pt"
    ).resolve()
    print()
    print("Training finished.")
    print(f"Expected weights: {weights}")
    print(
        "The analyze pipeline / predict script will pick this file up "
        "automatically via src/services/model_paths.py "
        "(or set YOLO_MODEL_PATH)."
    )


if __name__ == "__main__":
    train_model()
