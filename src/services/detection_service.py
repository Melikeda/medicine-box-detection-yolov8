from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from src.services.config import PipelineConfig
from src.services.detection import DetectedBox, detect_all_boxes

logger = logging.getLogger(__name__)


class DetectionService:
    """YOLO tabanlı ilaç kutusu tespiti ve crop işlemleri."""

    def __init__(
        self,
        config: PipelineConfig,
        model: YOLO,
    ) -> None:
        self.config = config
        self.model = model
        self._last_detection_used_fallback = False

    @property
    def last_detection_used_fallback(self) -> bool:
        return self._last_detection_used_fallback

    def predict(
        self,
        image_path: str | Path,
        *,
        confidence_threshold: float | None = None,
    ) -> Results | None:
        """Görüntü üzerinde YOLO tahmini çalıştırır."""
        image_path = Path(image_path)
        threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else self.config.confidence_threshold
        )

        prediction_results = self.model.predict(
            source=str(image_path),
            conf=threshold,
            save=False,
            verbose=False,
        )

        if not prediction_results:
            return None

        return prediction_results[0]

    def _detect_at_threshold(
        self,
        image_path: str | Path,
        confidence_threshold: float,
    ) -> list[DetectedBox]:
        prediction = self.predict(
            image_path=image_path,
            confidence_threshold=confidence_threshold,
        )

        if prediction is None:
            return []

        return detect_all_boxes(result=prediction)

    def detect_all(
        self,
        image_path: str | Path,
    ) -> list[DetectedBox]:
        """
        Fotoğraftaki tüm ilaç kutularını tespit eder ve crop eder.

        Standart eşikte sonuç yoksa veya zayıf/bulanık tespitlerde
        düşük güven fallback'i devreye girer.
        """
        self._last_detection_used_fallback = False

        primary_threshold = self.config.confidence_threshold
        fallback_threshold = self.config.fallback_confidence_threshold

        detected_boxes = self._detect_at_threshold(
            image_path=image_path,
            confidence_threshold=primary_threshold,
        )

        if fallback_threshold >= primary_threshold:
            return detected_boxes

        should_use_fallback = not detected_boxes

        if detected_boxes and not should_use_fallback:
            max_confidence = max(
                box.confidence for box in detected_boxes
            )
            # Bulanık fotoğraflarda düşük skorlu tek tespit olabilir;
            # fallback daha fazla kutu bulursa onu kullan.
            if max_confidence < 0.55:
                fallback_boxes = self._detect_at_threshold(
                    image_path=image_path,
                    confidence_threshold=fallback_threshold,
                )
                if len(fallback_boxes) > len(detected_boxes):
                    detected_boxes = fallback_boxes
                    should_use_fallback = True

        if not detected_boxes:
            detected_boxes = self._detect_at_threshold(
                image_path=image_path,
                confidence_threshold=fallback_threshold,
            )
            should_use_fallback = bool(detected_boxes)

        if should_use_fallback and detected_boxes:
            self._last_detection_used_fallback = True
            logger.info(
                "YOLO fallback modu: conf=%.2f ile %s kutu bulundu.",
                fallback_threshold,
                len(detected_boxes),
            )
            print(
                f"YOLO fallback modu: conf={fallback_threshold:.2f} "
                f"({len(detected_boxes)} kutu)"
            )

        return detected_boxes

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
