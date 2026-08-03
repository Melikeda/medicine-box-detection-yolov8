"""TİTCK eşleme ve CSV zenginleştirme birim testleri."""

from __future__ import annotations

import pandas as pd

from scripts.titck.manual_overrides import apply_manual_overrides
from scripts.titck.medicine_mapper import (
    category_from_atc,
    enrich_row_from_titck,
    find_best_titck_match,
    normalize_match_text,
    parse_dosage,
    parse_form,
    score_titck_row,
)


def _sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ilac_adi": "PAROL 500 MG TABLET",
                "atc_kodu": "N02BE01",
                "atc_adi": "PARACETAMOL",
                "durumu": "AKTIF",
            },
            {
                "ilac_adi": "APRANAX 275 MG FILM KAPLI TABLET",
                "atc_kodu": "M01AE02",
                "atc_adi": "NAPROXEN",
                "durumu": "AKTIF",
            },
            {
                "ilac_adi": "NUROFEN COLD FLU 200 MG FILM KAPLI TABLET",
                "atc_kodu": "M01AE51",
                "atc_adi": "IBUPROFEN, COMBINATIONS",
                "durumu": "AKTIF",
            },
            {
                "ilac_adi": "IOHEXOL 300 MG ENJEKSIYON",
                "atc_kodu": "V08AB02",
                "atc_adi": "IOHEXOL",
                "durumu": "AKTIF",
            },
        ]
    )


def test_normalize_match_text_strips_turkish_chars() -> None:
    assert normalize_match_text("A-Ferin Forte") == "A FERIN FORTE"


def test_parse_dosage_and_form() -> None:
    assert parse_dosage("APRANAX 275 MG FILM KAPLI TABLET") == "275 MG"
    assert parse_form("PAROL 500 MG TABLET") == "Tablet"


def test_score_prefers_exact_name_over_variant() -> None:
    base = score_titck_row("Nurofen", "Nurofen", "NUROFEN 200 MG TABLET")
    variant = score_titck_row("Nurofen", "Nurofen", "NUROFEN COLD FLU 200 MG TABLET")
    assert base > variant


def test_find_best_titck_match_apranax() -> None:
    match = find_best_titck_match(
        _sample_frame(),
        medicine_name="Apranax",
        brand_name="Apranax",
    )
    assert match is not None
    assert "NAPROXEN" in match.atc_adi.upper()


def test_enrich_row_fills_placeholder_fields() -> None:
    row = {
        "medicine_id": "MED009",
        "medicine_name": "Apranax",
        "brand_name": "Apranax",
        "active_ingredient": "VERIFY_FROM_OFFICIAL_LEAFLET",
        "dosage": "VERIFY_FROM_OFFICIAL_LEAFLET",
        "form": "VERIFY_FROM_OFFICIAL_LEAFLET",
        "category": "Ağrı Kesici",
    }
    enriched = enrich_row_from_titck(row, _sample_frame())
    assert enriched["active_ingredient"] == "Naproxen"
    assert enriched["dosage"] == "275 MG"
    assert enriched["form"] == "Film Kaplı Tablet"


def test_manual_override_nurofen() -> None:
    row = {
        "medicine_id": "MED011",
        "medicine_name": "Nurofen",
        "brand_name": "Nurofen",
        "active_ingredient": "VERIFY_FROM_OFFICIAL_LEAFLET",
        "dosage": "VERIFY_FROM_OFFICIAL_LEAFLET",
        "form": "VERIFY_FROM_OFFICIAL_LEAFLET",
        "category": "Ağrı Kesici",
    }
    frame = _sample_frame()
    enriched = apply_manual_overrides(enrich_row_from_titck(row, frame))
    assert enriched["active_ingredient"] == "Ibuprofen"
    assert enriched["dosage"] == "200 mg"


def test_category_from_atc_prefix() -> None:
    assert category_from_atc("N02BE01") == "Ağrı Kesici"
    assert category_from_atc("J01CR02") == "Antibiyotik"
