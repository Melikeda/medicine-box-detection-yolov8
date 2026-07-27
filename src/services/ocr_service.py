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

    def extract_candidates(
        self,
        cropped_image: np.ndarray,
        *,
        save_debug_outputs: bool = False,
    ) -> tuple[list[str], OCRPipelineResult]:
        """
        Kırpılmış görüntüden OCR aday metinlerini üretir.

        ocr_mode:
            fast     — tek rotasyon, standart varyantlar (~6 OCR)
            accurate — dört rotasyon + bulanık varyantlar (~52 OCR)
        """
        print(f"OCR modu: {self.config.ocr_mode}")

        pipeline_result = run_ocr_pipeline(
            reader=self.reader,
            image_input=cropped_image,
            scale_factor=self.config.ocr_scale_factor,
            minimum_confidence=self.config.minimum_ocr_confidence,
            rotation_angles=self.config.ocr_rotation_angles,
            blur_threshold=self.config.ocr_blur_threshold,
            save_preprocessed_images=save_debug_outputs,
            output_directory=(
                self.config.ocr_variants_directory
                if save_debug_outputs
                else None
            ),
        )

        candidate_texts = get_candidate_texts(
            pipeline_result=pipeline_result,
        )

        return candidate_texts, pipeline_result
