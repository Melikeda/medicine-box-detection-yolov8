"""Upload görsellerini analiz öncesi boyutlandırır."""

from __future__ import annotations

import io

from PIL import Image


def resize_image_bytes_if_large(
    file_bytes: bytes,
    *,
    max_dimension: int,
    suffix: str,
) -> tuple[bytes, bool]:
    """
    Uzun kenarı max_dimension üzerindeyse orantılı küçültür.

    Returns:
        (bytes, resized_flag)
    """
    if max_dimension <= 0:
        return file_bytes, False

    with Image.open(io.BytesIO(file_bytes)) as image:
        width, height = image.size
        longest = max(width, height)
        if longest <= max_dimension:
            return file_bytes, False

        scale = max_dimension / longest
        new_size = (
            max(1, int(width * scale)),
            max(1, int(height * scale)),
        )
        resized = image.convert("RGB").resize(
            new_size,
            Image.Resampling.LANCZOS,
        )

        output = io.BytesIO()
        save_format = _format_for_suffix(suffix)
        resized.save(output, format=save_format, quality=85)
        return output.getvalue(), True


def _format_for_suffix(suffix: str) -> str:
    normalized = suffix.lower().lstrip(".")
    if normalized in {"jpg", "jpeg"}:
        return "JPEG"
    if normalized == "png":
        return "PNG"
    if normalized == "webp":
        return "WEBP"
    return "JPEG"
