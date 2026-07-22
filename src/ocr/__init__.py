"""
OCR package for the AI-Powered Medicine Box Detection System.

This package provides reusable utilities for:

- Creating an EasyOCR reader
- Running the multi-variant OCR pipeline
- Generating OCR text candidates
- Cleaning OCR results
- Combining extracted texts
- Visualizing OCR detections
"""

from .ocr_pipeline import (
    OCRCandidate,
    OCRPipelineResult,
    create_ocr_variants,
    get_candidate_texts,
    load_ocr_image,
    run_ocr_pipeline,
)

from .ocr_reader import (
    create_ocr_reader,
    draw_ocr_results,
    read_text_from_image,
)

from .text_cleaner import (
    clean_text,
    combine_texts,
    extract_texts,
)


__all__ = [
    "OCRCandidate",
    "OCRPipelineResult",
    "create_ocr_variants",
    "get_candidate_texts",
    "load_ocr_image",
    "run_ocr_pipeline",
    "create_ocr_reader",
    "read_text_from_image",
    "draw_ocr_results",
    "clean_text",
    "extract_texts",
    "combine_texts",
]