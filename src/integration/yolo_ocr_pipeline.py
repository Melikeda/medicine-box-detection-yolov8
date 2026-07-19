from pathlib import Path
from typing import Any

import cv2
import easyocr
import numpy as np
from ultralytics import YOLO

from src.ocr.ocr_pipeline import run_ocr_pipeline
from src.ocr.text_cleaner import (
    combine_texts,
    extract_texts,
)


def load_yolo_model(
    model_path: str | Path,
) -> YOLO:
    """
    Eğitilmiş YOLO modelini yükler.
    """
    model_path = Path(model_path)

    if not model_path.exists():
        raise FileNotFoundError(
            f"YOLO model dosyası bulunamadı: {model_path}"
        )

    return YOLO(str(model_path))


def detect_medicine_boxes(
    model: YOLO,
    image_path: str | Path,
    confidence_threshold: float = 0.25,
) -> tuple[np.ndarray, list[Any]]:
    """
    Görüntüdeki ilaç kutularını YOLO ile tespit eder.

    Orijinal görüntüyü ve tespit edilen bounding box
    bilgilerini döndürür.
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Görüntü bulunamadı: {image_path}"
        )

    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(
            f"Görüntü OpenCV ile okunamadı: {image_path}"
        )

    prediction_results = model.predict(
        source=str(image_path),
        conf=confidence_threshold,
        verbose=False,
    )

    if not prediction_results:
        return image, []

    boxes = prediction_results[0].boxes

    if boxes is None:
        return image, []

    return image, list(boxes)


def crop_detected_box(
    image: np.ndarray,
    box: Any,
) -> np.ndarray:
    """
    YOLO bounding box koordinatlarına göre
    ilaç kutusunu görüntüden kırpar.
    """
    coordinates = box.xyxy[0].cpu().numpy()

    x1, y1, x2, y2 = map(
        int,
        coordinates,
    )

    image_height, image_width = image.shape[:2]

    x1 = max(0, min(x1, image_width))
    x2 = max(0, min(x2, image_width))
    y1 = max(0, min(y1, image_height))
    y2 = max(0, min(y2, image_height))

    if x2 <= x1 or y2 <= y1:
        raise ValueError(
            "Geçersiz bounding box koordinatları: "
            f"({x1}, {y1}, {x2}, {y2})"
        )

    cropped_image = image[
        y1:y2,
        x1:x2,
    ]

    return cropped_image


def run_yolo_ocr_pipeline(
    model: YOLO,
    reader: easyocr.Reader,
    image_path: str | Path,
    output_directory: str | Path,
    detection_confidence: float = 0.25,
    ocr_confidence: float = 0.70,
) -> list[dict[str, Any]]:
    """
    Tam YOLO + OCR entegrasyonunu çalıştırır.

    İşlem sırası:
    1. İlaç kutularını tespit eder.
    2. Her kutuyu crop eder.
    3. Crop görüntüsünü kaydeder.
    4. OCR pipeline çalıştırır.
    5. Metinleri güven skoruna göre filtreler.
    6. Metinleri temizler ve birleştirir.
    7. Sonuçları liste olarak döndürür.
    """
    output_directory = Path(output_directory)

    crop_directory = output_directory / "crops"
    preprocessed_directory = output_directory / "preprocessed"

    crop_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    preprocessed_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    image, detected_boxes = detect_medicine_boxes(
        model=model,
        image_path=image_path,
        confidence_threshold=detection_confidence,
    )

    pipeline_results: list[dict[str, Any]] = []

    for index, box in enumerate(
        detected_boxes,
        start=1,
    ):
        cropped_image = crop_detected_box(
            image=image,
            box=box,
        )

        crop_path = (
            crop_directory
            / f"medicine_box_{index}.jpg"
        )

        save_success = cv2.imwrite(
            str(crop_path),
            cropped_image,
        )

        if not save_success:
            raise IOError(
                f"Crop görüntüsü kaydedilemedi: {crop_path}"
            )

        preprocessed_path = (
            preprocessed_directory
            / f"medicine_box_{index}_preprocessed.jpg"
        )

        ocr_results = run_ocr_pipeline(
            reader=reader,
            image_path=crop_path,
            save_preprocessed_image=True,
            output_path=preprocessed_path,
        )

        cleaned_texts = extract_texts(
            ocr_results=ocr_results,
            minimum_confidence=ocr_confidence,
        )

        combined_text = combine_texts(
            cleaned_texts,
        )

        detection_score = float(
            box.conf[0].cpu().item()
        )

        class_id = int(
            box.cls[0].cpu().item()
        )

        coordinates = (
            box.xyxy[0]
            .cpu()
            .numpy()
            .astype(int)
            .tolist()
        )

        pipeline_results.append(
            {
                "detection_number": index,
                "class_id": class_id,
                "detection_confidence": detection_score,
                "bounding_box": coordinates,
                "crop_path": str(crop_path),
                "preprocessed_path": str(
                    preprocessed_path
                ),
                "texts": cleaned_texts,
                "combined_text": combined_text,
            }
        )

    return pipeline_results