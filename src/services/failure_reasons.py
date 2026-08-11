"""Basarisiz kutu analizi icin failure_reason + kullanici ipucu."""

from __future__ import annotations

from dataclasses import dataclass

from src.matching.text_normalizer import normalize_ocr_text
from src.ocr.ocr_pipeline import DEFAULT_BLUR_THRESHOLD, calculate_blur_score
from src.services.candidate_processor import (
    has_weak_ocr_candidates,
    max_candidate_alpha_length,
)

FailureReason = str

HINTS_TR: dict[str, str] = {
    "no_detection": (
        "Fotografta ilac kutusu tespit edilemedi. "
        "Kutuyu kadraja tam alin, yakindan ve iyi isikta cekin."
    ),
    "partial_box": (
        "Kutu kadrajda yarim kalmis olabilir. "
        "Kutunun tamamini fotografa sigdirip tekrar deneyin."
    ),
    "blurry": (
        "Goruntu bulanik gorunuyor. "
        "Telefonu sabitleyip net bir kare ile tekrar deneyin."
    ),
    "ocr_weak": (
        "Kutu uzerindeki yazi yeterince okunamadi. "
        "Daha yakindan, dik acida ve iyi isikta cekin."
    ),
    "low_confidence": (
        "Eslesme guveni dusuk. "
        "Daha net bir fotograf veya farkli bir aci deneyin."
    ),
    "not_in_catalog": (
        "Yazi okundu ancak katalogda guvenilir eslesme bulunamadi. "
        "Urun veritabaninda olmayabilir."
    ),
    "unknown": (
        "Bu kutu dogrulanamadi. "
        "Daha net, tam kadrajli bir fotograf deneyin."
    ),
    "error": (
        "Bu kutu analiz edilirken bir hata olustu. "
        "Tekrar deneyin."
    ),
}


@dataclass(frozen=True)
class FailureInfo:
    reason: FailureReason
    hint: str


def hint_for(reason: FailureReason) -> str:
    return HINTS_TR.get(reason, HINTS_TR["unknown"])


def is_bbox_partial(
    *,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    image_width: int,
    image_height: int,
    edge_margin_ratio: float = 0.02,
) -> bool:
    """Kutu cercevesi goruntu kenarina yapisiysa True."""
    if image_width <= 0 or image_height <= 0:
        return False

    margin_x = max(2, int(image_width * edge_margin_ratio))
    margin_y = max(2, int(image_height * edge_margin_ratio))

    return (
        x1 <= margin_x
        or y1 <= margin_y
        or x2 >= image_width - margin_x
        or y2 >= image_height - margin_y
    )


def classify_box_failure(
    *,
    status: str,
    matching_score: float,
    ocr_text: str | None,
    candidate_texts: list[str] | None = None,
    cropped_image=None,
    bounding_box=None,
    image_width: int | None = None,
    image_height: int | None = None,
    blur_threshold: float = DEFAULT_BLUR_THRESHOLD,
    minimum_plausible_match_score: float = 65.0,
) -> FailureInfo | None:
    """
    matched disindaki sonuclar icin failure_reason uretir.

    Oncelik: error → blurry → partial → ocr_weak →
    not_in_catalog / low_confidence / unknown
    """
    if status == "matched":
        return None

    if status == "error":
        return FailureInfo("error", hint_for("error"))

    candidates = candidate_texts or []
    if ocr_text and ocr_text.strip():
        candidates = list(candidates) + [ocr_text]

    # Blur (crop uzerinden)
    if cropped_image is not None:
        try:
            blur_score = calculate_blur_score(cropped_image)
            if blur_score < blur_threshold:
                return FailureInfo("blurry", hint_for("blurry"))
        except ValueError:
            pass

    # Yarim kutu (kenara yapisan bbox)
    if (
        bounding_box is not None
        and image_width is not None
        and image_height is not None
    ):
        if is_bbox_partial(
            x1=bounding_box.x1,
            y1=bounding_box.y1,
            x2=bounding_box.x2,
            y2=bounding_box.y2,
            image_width=image_width,
            image_height=image_height,
        ):
            return FailureInfo("partial_box", hint_for("partial_box"))

    # Zayif OCR
    if not candidates or has_weak_ocr_candidates(candidates):
        return FailureInfo("ocr_weak", hint_for("ocr_weak"))

    alpha_len = max_candidate_alpha_length(candidates)
    normalized = normalize_ocr_text(ocr_text or "")
    has_readable = bool(normalized) and alpha_len >= 6

    if status == "not_found" and has_readable:
        if matching_score >= minimum_plausible_match_score:
            return FailureInfo(
                "not_in_catalog",
                hint_for("not_in_catalog"),
            )
        return FailureInfo(
            "low_confidence",
            hint_for("low_confidence"),
        )

    if status == "not_medicine_box":
        if has_readable and matching_score < minimum_plausible_match_score:
            return FailureInfo(
                "low_confidence",
                hint_for("low_confidence"),
            )
        return FailureInfo("unknown", hint_for("unknown"))

    return FailureInfo("unknown", hint_for("unknown"))
