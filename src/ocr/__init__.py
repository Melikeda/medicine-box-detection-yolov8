"""
OCR package for the AI-Powered Medicine Box Detection System.

This package provides reusable utilities for:

- Creating an EasyOCR reader
- Running the OCR preprocessing pipeline
- Reading text from images
- Cleaning OCR results
- Combining extracted texts
- Visualizing OCR detections
"""

from .ocr_pipeline import (
    preprocess_image_for_ocr,
    run_ocr_pipeline,
)

from .ocr_reader import (
    create_ocr_reader,
    read_text_from_image,
    draw_ocr_results,
)

from .text_cleaner import (
    clean_text,
    extract_texts,
    combine_texts,
)

__all__ = [
    "preprocess_image_for_ocr",
    "run_ocr_pipeline",
    "create_ocr_reader",
    "read_text_from_image",
    "draw_ocr_results",
    "clean_text",
    "extract_texts",
    "combine_texts",
]