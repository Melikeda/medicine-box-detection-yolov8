"""SKRS marka eslesmesi olmayan populer OTC ilaclar ve ek TITCK markalari."""

from __future__ import annotations

import pandas as pd

from scripts.titck.medicine_mapper import (
    build_row_from_titck,
    find_best_titck_match,
    normalize_match_text,
    score_titck_row,
)

# TITCK SKRS listesinde marka adiyla bulunmayan raf ilaclari (prospektus/OTC).
POPULAR_MANUAL_ROWS: list[dict[str, str]] = [
    {
        "medicine_name": "Mucosolvan",
        "brand_name": "Mucosolvan",
        "active_ingredient": "Ambroxol HCl",
        "dosage": "30 mg/5 ml",
        "form": "Şurup",
        "category": "Öksürük İlacı",
    },
    {
        "medicine_name": "Mucosolvan Tablet",
        "brand_name": "Mucosolvan",
        "active_ingredient": "Ambroxol HCl",
        "dosage": "30 mg",
        "form": "Tablet",
        "category": "Öksürük İlacı",
    },
    {
        "medicine_name": "Bisolvon",
        "brand_name": "Bisolvon",
        "active_ingredient": "Bromhexine HCl",
        "dosage": "8 mg",
        "form": "Tablet",
        "category": "Öksürük İlacı",
    },
    {
        "medicine_name": "Mydocalm",
        "brand_name": "Mydocalm",
        "active_ingredient": "Tolperisone HCl",
        "dosage": "150 mg",
        "form": "Tablet",
        "category": "Kas Gevşetici",
    },
    {
        "medicine_name": "Mesulid",
        "brand_name": "Mesulid",
        "active_ingredient": "Nimesulide",
        "dosage": "100 mg",
        "form": "Tablet",
        "category": "Ağrı Kesici",
    },
    {
        "medicine_name": "Redoxon",
        "brand_name": "Redoxon",
        "active_ingredient": "Ascorbic Acid",
        "dosage": "1000 mg",
        "form": "Efervesan Tablet",
        "category": "Vitamin ve Mineral",
    },
    {
        "medicine_name": "Berocca",
        "brand_name": "Berocca",
        "active_ingredient": "Multivitamin / Mineral",
        "dosage": "Combined tablet",
        "form": "Efervesan Tablet",
        "category": "Vitamin ve Mineral",
    },
    {
        "medicine_name": "Sinutab",
        "brand_name": "Sinutab",
        "active_ingredient": "Paracetamol / Pseudoephedrine",
        "dosage": "500 mg / 30 mg",
        "form": "Tablet",
        "category": "Soğuk Algınlığı",
    },
    {
        "medicine_name": "Minol",
        "brand_name": "Minol",
        "active_ingredient": "Paracetamol",
        "dosage": "500 mg",
        "form": "Tablet",
        "category": "Ağrı Kesici",
    },
    {
        "medicine_name": "Strepsils",
        "brand_name": "Strepsils",
        "active_ingredient": "Amylmetacresol / Dichlorobenzyl Alcohol",
        "dosage": "Combined lozenge",
        "form": "Pastil",
        "category": "Soğuk Algınlığı",
    },
    {
        "medicine_name": "Deflamax",
        "brand_name": "Deflamax",
        "active_ingredient": "Diclofenac Potassium",
        "dosage": "50 mg",
        "form": "Tablet",
        "category": "Ağrı Kesici",
    },
    {
        "medicine_name": "Mobilat",
        "brand_name": "Mobilat",
        "active_ingredient": "Etofenamate",
        "dosage": "Combined gel",
        "form": "Jel",
        "category": "Kas ve Eklem",
    },
    {
        "medicine_name": "Pharmaton",
        "brand_name": "Pharmaton",
        "active_ingredient": "Multivitamin / Ginseng extract",
        "dosage": "Combined capsule",
        "form": "Kapsül",
        "category": "Vitamin ve Mineral",
    },
]

# SKRS'den tek en iyi urun secilecek markalar.
TITCK_SINGLE_BRAND_QUERIES: list[tuple[str, str]] = [
    ("Advil", "Ağrı Kesici"),
    ("Dolgit", "Kas ve Eklem"),
    ("Klacid", "Antibiyotik"),
    ("Differin", "Genel"),
]


def _next_id(start_index: int, offset: int) -> str:
    return f"MED{start_index + offset:03d}"


def _existing_keys(rows: list[dict[str, str]]) -> set[str]:
    return {normalize_match_text(row["medicine_name"]) for row in rows}


def _titck_brand_row(
    frame: pd.DataFrame,
    *,
    brand_query: str,
    category_hint: str,
    medicine_id: str,
) -> dict[str, str] | None:
    match = find_best_titck_match(
        frame,
        medicine_name=brand_query,
        brand_name=brand_query,
        min_score=80.0,
    )
    if match is None:
        active = frame[frame["durumu"].str.upper().eq("AKTIF")]
        best_score = 0.0
        best_row = None
        for _, titck_row in active.iterrows():
            ilac_adi = str(titck_row["ilac_adi"])
            if brand_query.upper() not in ilac_adi.upper():
                continue
            score = score_titck_row(brand_query, brand_query, ilac_adi)
            if score > best_score:
                best_score = score
                best_row = titck_row
        if best_row is None:
            return None
        return build_row_from_titck(
            medicine_id=medicine_id,
            ilac_adi=str(best_row["ilac_adi"]),
            atc_kodu=str(best_row["atc_kodu"]),
            atc_adi=str(best_row["atc_adi"]),
            category_hint=category_hint,
        )

    return build_row_from_titck(
        medicine_id=medicine_id,
        ilac_adi=match.ilac_adi,
        atc_kodu=match.atc_kodu,
        atc_adi=match.atc_adi,
        category_hint=category_hint,
    )


def append_popular_manual_rows(
    rows: list[dict[str, str]],
    frame: pd.DataFrame,
    *,
    start_index: int,
) -> list[dict[str, str]]:
    """Mevcut CSV'ye populer manual + secili TITCK satirlarini ekler."""
    used = _existing_keys(rows)
    appended: list[dict[str, str]] = []
    next_index = start_index

    for manual in POPULAR_MANUAL_ROWS:
        key = normalize_match_text(manual["medicine_name"])
        if key in used:
            continue
        row = {"medicine_id": _next_id(next_index, 0), **manual}
        appended.append(row)
        used.add(key)
        next_index += 1

    for brand_query, category_hint in TITCK_SINGLE_BRAND_QUERIES:
        brand_norm = normalize_match_text(brand_query)
        if brand_norm in {
            normalize_match_text(row.get("brand_name", ""))
            for row in rows + appended
        }:
            continue
        titck_row = _titck_brand_row(
            frame,
            brand_query=brand_query,
            category_hint=category_hint,
            medicine_id=_next_id(next_index, 0),
        )
        if titck_row is None:
            continue
        name_key = normalize_match_text(titck_row["medicine_name"])
        if name_key in used:
            continue
        appended.append(titck_row)
        used.add(name_key)
        next_index += 1

    return appended
