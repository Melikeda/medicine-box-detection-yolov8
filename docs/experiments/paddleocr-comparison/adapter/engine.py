"""
ARCHIVED — not imported by the Yolocilin product.

Snapshot of the PaddleOCR adapter used only for the EasyOCR vs PaddleOCR
trial. See docs/experiments/paddleocr-comparison/ and Report 26.
"""

from __future__ import annotations

import os
from typing import Any, Literal, Protocol, runtime_checkable

import cv2
import numpy as np

OCREngineName = Literal["easyocr", "paddleocr"]
SUPPORTED_OCR_ENGINES: tuple[OCREngineName, ...] = ("easyocr", "paddleocr")


class PaddleOCRNotInstalledError(ImportError):
    """Raised when OCR_ENGINE=paddleocr but optional deps are missing."""


@runtime_checkable
class OCRReader(Protocol):
    """Minimal reader used by ``run_ocr_on_variant``."""

    def readtext(
        self,
        image: Any,
        detail: int = 1,
        paragraph: bool = False,
    ) -> list[Any]:
        """Return EasyOCR-style ``[(bbox, text, confidence), ...]``."""


def normalize_engine_name(value: str | None) -> OCREngineName:
    engine = (value or "easyocr").strip().lower()
    if engine not in SUPPORTED_OCR_ENGINES:
        supported = ", ".join(SUPPORTED_OCR_ENGINES)
        raise ValueError(
            f"Unknown OCR engine {value!r}. Supported: {supported}."
        )
    return engine  # type: ignore[return-value]


def paddleocr_is_available() -> bool:
    try:
        import paddleocr  # noqa: F401
    except ImportError:
        return False
    return True


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bbox_from_poly(poly: Any) -> list[list[float]]:
    """Convert a polygon/box to EasyOCR's four-point bbox."""
    if poly is None:
        return [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]

    if isinstance(poly, np.ndarray):
        points = poly.reshape(-1, 2).tolist()
    elif isinstance(poly, (list, tuple)):
        if len(poly) == 4 and all(isinstance(v, (int, float)) for v in poly):
            x1, y1, x2, y2 = (float(v) for v in poly)
            points = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
        else:
            points = []
            for item in poly:
                if isinstance(item, (list, tuple, np.ndarray)) and len(item) >= 2:
                    points.append([float(item[0]), float(item[1])])
    else:
        points = []

    if len(points) >= 4:
        return points[:4]
    if len(points) == 2:
        (x1, y1), (x2, y2) = points
        return [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
    return [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]


def _item_to_easyocr(item: Any) -> tuple[list[list[float]], str, float] | None:
    """Parse one PaddleOCR 2.x line: ``[bbox, (text, conf)]``."""
    if not isinstance(item, (list, tuple)) or len(item) < 2:
        return None
    bbox = _bbox_from_poly(item[0])
    payload = item[1]
    if isinstance(payload, (list, tuple)) and len(payload) >= 1:
        text = str(payload[0]).strip()
        confidence = _as_float(payload[1] if len(payload) > 1 else 0.0)
    else:
        text = str(payload).strip()
        confidence = 0.0
    if not text:
        return None
    return bbox, text, confidence


def _looks_like_detection_line(item: Any) -> bool:
    if not isinstance(item, (list, tuple)) or len(item) < 2:
        return False
    payload = item[1]
    if isinstance(payload, str):
        return True
    if isinstance(payload, (list, tuple)) and payload:
        return isinstance(payload[0], str)
    return False


def paddle_result_to_easyocr(raw: Any) -> list[tuple[list[list[float]], str, float]]:
    """
    Normalize PaddleOCR 2.x ``ocr()`` and 3.x ``predict()`` output
    into EasyOCR ``readtext(detail=1)`` tuples.
    """
    converted: list[tuple[list[list[float]], str, float]] = []
    if raw is None:
        return converted

    if isinstance(raw, dict) or (
        not isinstance(raw, (list, tuple, np.ndarray)) and hasattr(raw, "keys")
    ):
        converted.extend(_from_paddle_mapping(raw))
        return converted

    if isinstance(raw, (list, tuple)):
        if not raw:
            return converted
        if _looks_like_detection_line(raw[0]):
            for item in raw:
                line = _item_to_easyocr(item)
                if line is not None:
                    converted.append(line)
            return converted
        for page in raw:
            converted.extend(paddle_result_to_easyocr(page))
        return converted

    converted.extend(_from_paddle_mapping(raw))
    return converted


def _get_attr_or_key(obj: Any, name: str) -> Any:
    """Prefer mapping .get(); PaddleX OCRResult hides values behind keys."""
    if hasattr(obj, "get"):
        try:
            value = obj.get(name)
            if value is not None:
                return value
        except TypeError:
            pass
    if isinstance(obj, dict):
        return obj.get(name)
    if hasattr(obj, name):
        value = getattr(obj, name)
        if value is not None:
            return value
    return None


def _from_paddle_mapping(
    obj: Any,
) -> list[tuple[list[list[float]], str, float]]:
    texts = (
        _get_attr_or_key(obj, "rec_texts")
        or _get_attr_or_key(obj, "rec_text")
        or []
    )
    scores = (
        _get_attr_or_key(obj, "rec_scores")
        or _get_attr_or_key(obj, "rec_score")
        or []
    )
    polys = (
        _get_attr_or_key(obj, "rec_polys")
        or _get_attr_or_key(obj, "dt_polys")
        or _get_attr_or_key(obj, "rec_poly")
        or []
    )
    if isinstance(texts, str):
        texts = [texts]
        scores = [scores] if not isinstance(scores, (list, tuple, np.ndarray)) else scores
        polys = [polys] if polys is not None and not isinstance(polys, (list, tuple, np.ndarray)) else polys

    converted: list[tuple[list[list[float]], str, float]] = []
    if not texts:
        nested = _get_attr_or_key(obj, "json") or _get_attr_or_key(obj, "res")
        if nested is not None and nested is not obj:
            return _from_paddle_mapping(nested)
        return converted

    for index, text in enumerate(texts):
        cleaned = str(text).strip()
        if not cleaned:
            continue
        score = _as_float(scores[index] if index < len(scores) else 0.0)
        poly = polys[index] if index < len(polys) else None
        converted.append((_bbox_from_poly(poly), cleaned, score))
    return converted


def _to_rgb(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    if image.ndim == 3 and image.shape[2] == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


class PaddleOCRReader:
    """
    Wraps PaddleOCR so callers can use EasyOCR's ``readtext()`` contract.

    Supports PaddleOCR 2.x (``ocr()``) and 3.x (``predict()``).
    """

    def __init__(self, inner: Any) -> None:
        self._inner = inner

    def readtext(
        self,
        image: Any,
        detail: int = 1,
        paragraph: bool = False,
    ) -> list[Any]:
        del paragraph
        array = np.asarray(image)
        rgb = _to_rgb(array)
        raw = self._invoke(rgb)
        results = paddle_result_to_easyocr(raw)
        if detail == 0:
            return [text for _, text, _ in results]
        return results

    def _invoke(self, image: np.ndarray) -> Any:
        if hasattr(self._inner, "predict"):
            try:
                return self._inner.predict(image)
            except TypeError:
                pass
        if hasattr(self._inner, "ocr"):
            try:
                return self._inner.ocr(image, cls=True)
            except TypeError:
                return self._inner.ocr(image)
        raise RuntimeError("PaddleOCR instance has neither predict() nor ocr().")


def _configure_paddle_cpu_runtime() -> None:
    """
    PaddlePaddle 3.3.x CPU + oneDNN + PIR crashes on Windows:

    ConvertPirAttribute2RuntimeAttribute not support ArrayAttribute<DoubleAttribute>

    PaddleX defaults run_mode=mkldnn; FLAGS_use_mkldnn=0 is ignored.
    Disable MKLDNN before constructing PaddleOCR.
    """
    os.environ.setdefault("FLAGS_use_mkldnn", "0")
    os.environ.setdefault("PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT", "0")


def _build_paddle_instance(*, use_gpu: bool) -> Any:
    _configure_paddle_cpu_runtime()
    try:
        from paddleocr import PaddleOCR
    except ImportError as exc:
        raise PaddleOCRNotInstalledError(
            "PaddleOCR is not installed. From the repo root, with venv active:\n"
            "  pip install -r requirements-paddleocr.txt\n"
            "or:  .\\scripts\\setup-paddleocr.ps1\n"
            "Default engine (EasyOCR) is unchanged until OCR_ENGINE=paddleocr."
        ) from exc

    device = "gpu" if use_gpu else "cpu"
    cpu_safe = {
        "lang": "en",
        "device": device,
        "use_doc_orientation_classify": False,
        "use_doc_unwarping": False,
        "use_textline_orientation": False,
    }
    if not use_gpu:
        cpu_safe["enable_mkldnn"] = False

    constructors = (
        lambda: PaddleOCR(**cpu_safe),
        lambda: PaddleOCR(lang="en", device=device, enable_mkldnn=False),
        lambda: PaddleOCR(lang="latin", device=device, enable_mkldnn=False),
        lambda: PaddleOCR(
            use_angle_cls=True,
            lang="en",
            use_gpu=use_gpu,
            show_log=False,
        ),
        lambda: PaddleOCR(lang="en"),
    )
    last_error: Exception | None = None
    for build in constructors:
        try:
            return build()
        except (TypeError, ValueError) as exc:
            last_error = exc
            continue
    raise RuntimeError(
        f"Could not construct PaddleOCR with this package version: {last_error}"
    )


def create_paddle_ocr_reader(*, use_gpu: bool = False) -> PaddleOCRReader:
    return PaddleOCRReader(_build_paddle_instance(use_gpu=use_gpu))
