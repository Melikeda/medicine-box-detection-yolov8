"""Görüntüden 1D/2D barkod okur (zxing-cpp)."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import cv2
import numpy as np

from src.barcode.normalize import is_plausible_barcode, normalize_barcode

logger = logging.getLogger(__name__)

_zxingcpp = None
_zxing_checked = False


@dataclass(frozen=True)
class DecodedBarcode:
    """Tek bir çözülmüş barkod."""

    text: str
    normalized: str
    format: str


def decode_barcodes(image: np.ndarray) -> list[DecodedBarcode]:
    """
    OpenCV BGR/gray görüntüden barkodları okur.

    İlk deneme başarısızsa büyütülmüş kopya denenir (küçük/uzak kodlar).
    zxing-cpp yoksa boş liste döner; OCR yolu kesilmez.
    """
    if image is None or image.size == 0:
        return []
    if _load_zxing() is None:
        return []

    try:
        rgb = _to_rgb(image)
        found = _read_unique(rgb)
        if found:
            return found

        height, width = rgb.shape[:2]
        if max(height, width) < 1200:
            scaled = cv2.resize(
                rgb,
                None,
                fx=2.0,
                fy=2.0,
                interpolation=cv2.INTER_CUBIC,
            )
            found = _read_unique(scaled)
            if found:
                return found

        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        return _read_unique(gray)
    except Exception:
        logger.warning("Barkod çözme atlandı; OCR devam eder.", exc_info=True)
        return []


def decode_barcode_texts(image: np.ndarray) -> list[str]:
    """Yalnızca normalize edilmiş, geçerli barkod metinlerini döndürür."""
    return [item.normalized for item in decode_barcodes(image)]


def _to_rgb(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    if image.ndim == 3 and image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
    if image.ndim == 3 and image.shape[2] == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    raise ValueError("Desteklenmeyen görüntü şekli.")


def _load_zxing():
    global _zxingcpp, _zxing_checked
    if _zxing_checked:
        return _zxingcpp
    _zxing_checked = True
    try:
        import zxingcpp

        _zxingcpp = zxingcpp
    except ImportError:
        logger.warning(
            "zxing-cpp yüklü değil; kamera taraması OCR ile devam eder."
        )
        _zxingcpp = None
    return _zxingcpp


def _read_unique(image: np.ndarray) -> list[DecodedBarcode]:
    zxingcpp = _load_zxing()
    if zxingcpp is None:
        return []

    raw_results = zxingcpp.read_barcodes(image)
    decoded: list[DecodedBarcode] = []
    seen: set[str] = set()

    for result in raw_results:
        text = str(getattr(result, "text", "") or "").strip()
        if not text:
            continue
        normalized = normalize_barcode(text)
        if not is_plausible_barcode(normalized):
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        format_name = _format_name(result)
        decoded.append(
            DecodedBarcode(
                text=text,
                normalized=normalized,
                format=format_name,
            )
        )

    return decoded


def _format_name(result: object) -> str:
    raw_format = getattr(result, "format", None)
    if raw_format is None:
        return "unknown"
    name = getattr(raw_format, "name", None)
    if isinstance(name, str) and name:
        return name
    return str(raw_format)
