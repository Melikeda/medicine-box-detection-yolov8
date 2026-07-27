from __future__ import annotations

from pathlib import Path

import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from src.services.config import PipelineConfig
from src.services.detection import DetectedBox, detect_all_boxes


class DetectionService:
    """YOLO tabanlı ilaç kutusu tespiti ve crop işlemleri."""

    def __init__(
        self,
        config: PipelineConfig,
        model: YOLO,
    ) -> None:
        self.config = config
        self.model = model

    def predict(
        self,
        image_path: str | Path,
    ) -> Results | None:
        """Görüntü üzerinde YOLO tahmini çalıştırır."""
        image_path = Path(image_path)

        prediction_results = self.model.predict(
            source=str(image_path),
            conf=self.config.confidence_threshold,
            save=False,
            verbose=False,
        )

        if not prediction_results:
            return None

        return prediction_results[0]

    def detect_all(
        self,
        image_path: str | Path,
    ) -> list[DetectedBox]:
        """
        Fotoğraftaki tüm ilaç kutularını tespit eder ve crop eder.

        Sonuçlar YOLO confidence değerine göre azalan sırada döner.
        """
        prediction = self.predict(image_path=image_path)

        if prediction is None:
            return []

        return detect_all_boxes(result=prediction)

    def detect_and_crop(
        self,
        image_path: str | Path,
    ) -> tuple[np.ndarray, float] | None:
        """
        En yüksek güven skorlu tek kutuyu döndürür (geriye dönük uyumluluk).
        """
        detected_boxes = self.detect_all(image_path=image_path)

        if not detected_boxes:
            return None

        best = detected_boxes[0]
        return best.cropped_image, best.confidence
