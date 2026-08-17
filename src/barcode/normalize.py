"""Barkod metnini katalog araması için normalize eder."""

from __future__ import annotations

import re

_NON_DIGIT = re.compile(r"\D+")
_GS1_GTIN = re.compile(r"(?:^|[^\d])01(\d{14})")
# mobile_scanner / zxing AIM kimliği: ]C1 (GS1-128), ]d2 (DataMatrix), ]E0 (EAN-13)
_AIM_IDENTIFIER = re.compile(r"^\][A-Za-z]\d")


def normalize_barcode(raw: str | None) -> str:
    """
    EAN-13 / UPC / GTIN / GS1 DataMatrix metnini rakam dizisine çevirir.

    Türkiye ilaç kutularındaki 1D EAN-13 ve İTS DataMatrix (AI 01 + GTIN)
    aynı katalog anahtarına indirgenir.
    """
    if raw is None:
        return ""

    text = _strip_aim_identifier(raw.strip())
    if not text:
        return ""

    gtin14 = _extract_gs1_gtin14(text)
    if gtin14:
        return _gtin14_to_catalog_key(gtin14)

    digits = _NON_DIGIT.sub("", text)
    if not digits:
        return ""

    if len(digits) == 14:
        return _gtin14_to_catalog_key(digits)

    if len(digits) == 12:
        return f"0{digits}"

    return digits


def is_plausible_barcode(digits: str | None) -> bool:
    """Katalog aramasına uygun uzunlukta rakam dizisi mi?"""
    if not digits or not digits.isdigit():
        return False
    return 8 <= len(digits) <= 14


def barcode_lookup_keys(raw: str | None) -> list[str]:
    """Aynı paket için denenmesi gereken katalog anahtarları."""
    keys: list[str] = []
    seen: set[str] = set()

    def _add(value: str) -> None:
        if value and value not in seen and is_plausible_barcode(value):
            seen.add(value)
            keys.append(value)

    primary = normalize_barcode(raw)
    _add(primary)

    if raw is None:
        return keys

    prepared = _strip_aim_identifier(raw.strip())
    digits = _NON_DIGIT.sub("", prepared)
    if not digits:
        return keys

    _add(normalize_barcode(digits))
    if len(digits) >= 14:
        _add(normalize_barcode(digits[-13:]))
        _add(normalize_barcode(digits[-14:]))
    if len(digits) == 14 and digits.startswith("0"):
        _add(digits[1:])
    if len(digits) == 13:
        _add("0" + digits)
    return keys


def _strip_aim_identifier(text: str) -> str:
    """Barkod okuyucunun eklediği ]C1 / ]E0 gibi AIM önekini kaldırır."""
    if _AIM_IDENTIFIER.match(text):
        return text[3:]
    return text


def _extract_gs1_gtin14(text: str) -> str | None:
    match = _GS1_GTIN.search(text)
    if match:
        return match.group(1)

    digits = _NON_DIGIT.sub("", text)
    if digits.startswith("01") and len(digits) >= 16:
        return digits[2:16]
    return None


def _gtin14_to_catalog_key(gtin14: str) -> str:
    if len(gtin14) == 14 and gtin14.startswith("0"):
        return gtin14[1:]
    return gtin14
