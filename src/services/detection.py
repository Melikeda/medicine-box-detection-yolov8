from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from ultralytics.engine.results import Results


@dataclass(frozen=True)
class BoundingBox:
    """YOLO bounding box koordinatları (piksel)."""

    x1: int
    y1: int
    x2: int
    y2: int

    def to_dict(self) -> dict[str, int]:
        return {
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
        }


@dataclass
class DetectedBox:
    """Tek bir YOLO tespiti ve kırpılmış görüntü."""

    cropped_image: np.ndarray
    confidence: float
    bounding_box: BoundingBox


def _clip_coordinates(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    image_width: int,
    image_height: int,
) -> BoundingBox | None:
    x1 = max(0, min(x1, image_width))
    x2 = max(0, min(x2, image_width))
    y1 = max(0, min(y1, image_height))
    y2 = max(0, min(y2, image_height))

    if x2 <= x1 or y2 <= y1:
        return None

    return BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)


def detect_all_boxes(
    result: Results,
) -> list[DetectedBox]:
    """
    YOLO NMS sonucundaki tüm kutuları confidence'a göre sıralı döndürür.

    Yalnızca geçerli crop üretilebilen kutular listelenir.
    """
    if result.orig_img is None:
        return []

    if result.boxes is None or len(result.boxes) == 0:
        return []

    original_image = result.orig_img
    image_height, image_width = original_image.shape[:2]

    confidence_values = result.boxes.conf.detach().cpu().numpy()
    sorted_indices = confidence_values.argsort()[::-1]

    detected_boxes: list[DetectedBox] = []

    for box_index in sorted_indices:
        box = result.boxes[int(box_index)]
        coordinates = box.xyxy[0].detach().cpu().numpy()
        x1, y1, x2, y2 = map(int, coordinates)

        bounding_box = _clip_coordinates(
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            image_width=image_width,
            image_height=image_height,
        )

        if bounding_box is None:
            continue

        cropped_image = original_image[
            bounding_box.y1 : bounding_box.y2,
            bounding_box.x1 : bounding_box.x2,
        ]

        if cropped_image.size == 0:
            continue

        confidence = float(box.conf[0].detach().cpu().item())

        detected_boxes.append(
            DetectedBox(
                cropped_image=cropped_image,
                confidence=confidence,
                bounding_box=bounding_box,
            )
        )

    return detected_boxes


def crop_best_detection(
    result: Results,
) -> tuple[np.ndarray, float] | None:
    """
    En yüksek güven skoruna sahip tek kutuyu döndürür.

    Geriye dönük uyumluluk için korunmuştur.
    """
    detected_boxes = detect_all_boxes(result)

    if not detected_boxes:
        return None

    best = detected_boxes[0]
    return best.cropped_image, best.confidence
