"""Performans yapılandırması ve OCR erken çıkış testleri."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np

from src.ocr.ocr_pipeline import OCRPipelineResult, run_ocr_pipeline
from src.services.config import PipelineConfig


def test_fast_mode_reduces_rotations_and_scale() -> None:
    config = PipelineConfig(ocr_mode="fast")
    assert config.ocr_rotation_angles == (0, 90)
    assert config.ocr_scale_factor == 1.5
    assert config.ocr_early_exit is True
    assert config.ocr_limited_variants is True


def test_accurate_mode_keeps_full_search_space() -> None:
    config = PipelineConfig(ocr_mode="accurate")
    assert config.ocr_rotation_angles == (0, 90, 180, 270)
    assert config.ocr_scale_factor == 2.0
    assert config.ocr_early_exit is False
    assert config.ocr_limited_variants is False


@patch("src.ocr.ocr_pipeline.run_ocr_on_variant")
@patch("src.ocr.ocr_pipeline.create_ocr_variants")
def test_run_ocr_pipeline_early_exit(
    mock_create_variants: MagicMock,
    mock_run_ocr: MagicMock,
) -> None:
    mock_create_variants.return_value = {
        "v1": np.zeros((10, 10, 3), dtype=np.uint8),
        "v2": np.zeros((10, 10, 3), dtype=np.uint8),
        "v3": np.zeros((10, 10, 3), dtype=np.uint8),
    }
    mock_run_ocr.return_value = [
        ([[0, 0], [1, 0], [1, 1], [0, 1]], "PAROL", 0.9),
    ]

    stop_after = {"count": 0}

    def should_stop(texts: list[str]) -> bool:
        stop_after["count"] += 1
        return len(texts) > 0

    reader = MagicMock()
    result = run_ocr_pipeline(
        reader=reader,
        image_input=np.zeros((20, 20, 3), dtype=np.uint8),
        limited_variants=True,
        should_stop_after_variant=should_stop,
    )

    assert isinstance(result, OCRPipelineResult)
    assert result.early_exit is True
    assert result.variants_processed == 1
    assert result.variants_total == 3
    assert mock_run_ocr.call_count == 1


def test_resize_image_bytes_if_large() -> None:
    from PIL import Image
    import io

    from backend.app.services.image_optimizer import (
        resize_image_bytes_if_large,
    )

    image = Image.new("RGB", (2000, 1500), color=(255, 0, 0))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    original = buffer.getvalue()

    resized_bytes, was_resized = resize_image_bytes_if_large(
        original,
        max_dimension=1280,
        suffix=".jpg",
    )

    assert was_resized is True
    with Image.open(io.BytesIO(resized_bytes)) as resized_image:
        assert max(resized_image.size) <= 1280
