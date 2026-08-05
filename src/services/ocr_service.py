from collections.abc import Callable

import easyocr
import numpy as np

from src.ocr.ocr_pipeline import (
    OCRPipelineResult,
    get_candidate_texts,
    run_ocr_pipeline,
)
from src.services.config import PipelineConfig


class OCRService:
    """EasyOCR tabanlı metin çıkarma servisi."""

    def __init__(
        self,
        config: PipelineConfig,
        reader: easyocr.Reader,
    ) -> None:
        self.config = config
        self.reader = reader

    def analyze_crop(
        self,
        cropped_image: np.ndarray,
        *,
        box_index: int | None = None,
        save_debug_outputs: bool = False,
        debug_subdirectory: str | None = None,
        should_stop_after_variant: (
            Callable[[list[str]], bool] | None
        ) = None,
        rotation_angles: tuple[int, ...] | None = None,
        scale_factor: float | None = None,
        limited_variants: bool | None = None,
        blur_threshold: float | None = None,
    ) -> tuple[list[str], OCRPipelineResult]:
        """
        Tek bir crop görüntüsünden OCR aday metinlerini üretir.

        Her crop kendi blur skoruna göre ayrı değerlendirilir.
        """
        if box_index is not None:
            print(f"OCR modu: {self.config.ocr_mode} (kutu {box_index})")
        else:
            print(f"OCR modu: {self.config.ocr_mode}")

        output_directory = None
        if save_debug_outputs and debug_subdirectory:
            output_directory = (
                self.config.ocr_variants_directory / debug_subdirectory
            )

        pipeline_result = run_ocr_pipeline(
            reader=self.reader,
            image_input=cropped_image,
            scale_factor=scale_factor or self.config.ocr_scale_factor,
            minimum_confidence=self.config.minimum_ocr_confidence,
            rotation_angles=(
                rotation_angles or self.config.ocr_rotation_angles
            ),
            blur_threshold=(
                blur_threshold
                if blur_threshold is not None
                else self.config.ocr_blur_threshold
            ),
            limited_variants=(
                limited_variants
                if limited_variants is not None
                else self.config.ocr_limited_variants
            ),
            save_preprocessed_images=save_debug_outputs,
            output_directory=output_directory,
            should_stop_after_variant=should_stop_after_variant,
        )

        candidate_texts = get_candidate_texts(
            pipeline_result=pipeline_result,
        )

        return candidate_texts, pipeline_result

    def extract_candidates(
        self,
        cropped_image: np.ndarray,
        *,
        save_debug_outputs: bool = False,
    ) -> tuple[list[str], OCRPipelineResult]:
        """Geriye dönük uyumluluk alias'ı."""
        return self.analyze_crop(
            cropped_image=cropped_image,
            save_debug_outputs=save_debug_outputs,
        )
