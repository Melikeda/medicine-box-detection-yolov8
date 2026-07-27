from pathlib import Path

import numpy as np
from ultralytics import YOLO

from src.services.config import PipelineConfig
from src.services.detection import crop_best_detection


class DetectionService:
    """YOLO tabanlı ilaç kutusu tespiti ve crop işlemleri."""

    def __init__(
        self,
        config: PipelineConfig,
        model: YOLO,
    ) -> None:
        self.config = config
        self.model = model

    def detect_and_crop(
        self,
        image_path: str | Path,
    ) -> tuple[np.ndarray, float] | None:
        """
        Görüntüdeki ilaç kutusunu tespit eder ve en iyi bbox'ı kırpar.

        Returns:
            (kırpılmış görüntü, YOLO güven skoru) veya None.
        """
        image_path = Path(image_path)

        prediction_results = self.model.predict(
            source=str(image_path),
            conf=self.config.confidence_threshold,
            save=False,
            verbose=False,
        )

        if not prediction_results:
            return None

        return crop_best_detection(result=prediction_results[0])
