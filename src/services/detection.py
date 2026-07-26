import numpy as np
from ultralytics.engine.results import Results


def crop_best_detection(
    result: Results,
) -> tuple[np.ndarray, float] | None:
    """
    YOLO sonucundaki en yüksek güven skoruna sahip
    bounding box'ı seçer ve görüntüyü kırpar.

    Returns:
        (kırpılmış görüntü, YOLO güven skoru) veya None.
    """
    if result.orig_img is None:
        return None

    if result.boxes is None:
        return None

    if len(result.boxes) == 0:
        return None

    original_image = result.orig_img
    image_height, image_width = original_image.shape[:2]

    confidence_values = (
        result.boxes.conf.detach().cpu().numpy()
    )

    best_box_index = int(confidence_values.argmax())
    best_box = result.boxes[best_box_index]

    coordinates = (
        best_box.xyxy[0].detach().cpu().numpy()
    )

    x1, y1, x2, y2 = map(int, coordinates)

    x1 = max(0, min(x1, image_width))
    x2 = max(0, min(x2, image_width))
    y1 = max(0, min(y1, image_height))
    y2 = max(0, min(y2, image_height))

    if x2 <= x1 or y2 <= y1:
        return None

    cropped_image = original_image[y1:y2, x1:x2]

    if cropped_image.size == 0:
        return None

    confidence = float(
        best_box.conf[0].detach().cpu().item()
    )

    return cropped_image, confidence
