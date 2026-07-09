from pathlib import Path
from ultralytics import YOLO


MODEL_PATH = Path("runs/detect/runs/detect/medicine_box_yolov8n-2/weights/best.pt")
SOURCE_PATH = Path("data/dataset/test/images")
OUTPUT_PROJECT = Path("runs/predict")
OUTPUT_NAME = "medicine_box_predictions"
CONFIDENCE_THRESHOLD = 0.60


def run_prediction() -> None:
    """
    Runs prediction using the trained YOLOv8 model on test images.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Source path not found: {SOURCE_PATH}")

    print("\nYOLOv8 Prediction Started")
    print("-------------------------")
    print(f"Model      : {MODEL_PATH}")
    print(f"Source     : {SOURCE_PATH}")
    print(f"Confidence : {CONFIDENCE_THRESHOLD}")

    model = YOLO(str(MODEL_PATH))

    results = model.predict(
        source=str(SOURCE_PATH),
        conf=CONFIDENCE_THRESHOLD,
        save=True,
        project=str(OUTPUT_PROJECT),
        name=OUTPUT_NAME,
        exist_ok=True,
    )

    print("\nYOLOv8 Prediction Completed")
    print("---------------------------")
    print(f"Output folder: {OUTPUT_PROJECT / OUTPUT_NAME}")
    print(f"Processed images: {len(results)}")


if __name__ == "__main__":
    run_prediction()