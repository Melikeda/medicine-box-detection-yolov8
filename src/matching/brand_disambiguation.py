"""Ayni marka ailesindeki SKU'lari OCR kanitina gore ayirt eder.

Parol vs Parol Plus, Majezik vs Gargara, Dolorex vs Jel gibi
beraberliklerde uzun isim tercihi yerine form/varyant kaniti kullanir.
"""

from __future__ import annotations

from src.matching.medicine_matcher import (
    calculate_medicine_score,
    normalize_text,
)

# (medicine, score, ocr_text) — candidate_processor.MatchRecord ile ayni sekil
MatchRecord = tuple[dict[str, str], float, str]

# Urun adi / OCR'da varyant veya form ayirici token'lar.
VARIANT_FORM_TOKENS = frozenset(
    {
        "plus",
        "duo",
        "forte",
        "fort",
        "extra",
        "cold",
        "flu",
        "gargara",
        "gargle",
        "jel",
        "gel",
        "krem",
        "cream",
        "merhem",
        "sprey",
        "spray",
        "surup",
        "syrup",
        "suspension",
        "damla",
        "sr",
        "retard",
        "kapsul",
        "capsule",
    }
)

TABLET_TOKENS = frozenset(
    {
        "tablet",
        "tablets",
        "tablot",
        "film",
        "kapli",
        "kaplı",
        "coated",
        "filmtablet",
    }
)

GEL_TOKENS = frozenset({"jel", "gel"})
GARGLE_TOKENS = frozenset({"gargara", "gargle"})
PLUS_TOKENS = frozenset({"plus"})
DUO_TOKENS = frozenset({"duo"})

SCORE_EPSILON = 2.0


def _token_set(text: str) -> set[str]:
    normalized = normalize_text(text)
    if not normalized:
        return set()
    return set(normalized.split())


def join_evidence_text(evidence_texts: list[str]) -> str:
    """Ham OCR adaylarini tek kanit metninde birlestirir."""
    parts = [
        normalize_text(text)
        for text in evidence_texts
        if text and text.strip()
    ]
    return " ".join(parts)


def medicine_variant_tokens(medicine: dict[str, str]) -> set[str]:
    """medicine_name + form icindeki ayirici token'lar."""
    name = medicine.get("medicine_name", "") or ""
    form = medicine.get("form", "") or ""
    brand = medicine.get("brand_name", "") or ""

    name_tokens = _token_set(name)
    brand_tokens = _token_set(brand)
    form_tokens = _token_set(form)

    extras = (name_tokens | form_tokens) - brand_tokens
    return extras & VARIANT_FORM_TOKENS


def is_base_sku(medicine: dict[str, str]) -> bool:
    """Marka ile ayni veya varyant token'i olmayan temel SKU."""
    name = normalize_text(medicine.get("medicine_name", "") or "")
    brand = normalize_text(medicine.get("brand_name", "") or "")
    if not name:
        return False
    if brand and name == brand:
        return True
    return not medicine_variant_tokens(medicine)


def evidence_alignment_boost(
    medicine: dict[str, str],
    evidence_text: str,
) -> float:
    """
    Form/varyant kanitina gore -20..+20 arasi skor ayari.

    Pozitif: OCR kaniti bu SKU'yu destekliyor.
    Negatif: OCR kaniti baska bir varyanti isaret ediyor.
    """
    evidence_tokens = _token_set(evidence_text)
    if not evidence_tokens:
        return 0.0

    name = normalize_text(medicine.get("medicine_name", "") or "")
    form = normalize_text(medicine.get("form", "") or "")
    dosage = normalize_text(medicine.get("dosage", "") or "")
    catalog_blob = f"{name} {form} {dosage}"
    catalog_tokens = _token_set(catalog_blob)
    variants = medicine_variant_tokens(medicine)

    boost = 0.0

    if variants:
        if variants & evidence_tokens:
            boost += 15.0
        else:
            boost -= 10.0
    else:
        # Temel SKU: OCR'da baska varyant yoksa tercih et.
        if evidence_tokens & VARIANT_FORM_TOKENS:
            # Ornek: OCR'da "plus" var ama bu Parol (base) — cezalandir.
            if evidence_tokens & (PLUS_TOKENS | DUO_TOKENS | GARGLE_TOKENS | GEL_TOKENS):
                if not (
                    (evidence_tokens & GEL_TOKENS and catalog_tokens & GEL_TOKENS)
                    or (
                        evidence_tokens & GARGLE_TOKENS
                        and catalog_tokens & GARGLE_TOKENS
                    )
                ):
                    boost -= 8.0
        else:
            boost += 8.0

    is_tablet_sku = bool(catalog_tokens & TABLET_TOKENS) or (
        "tablet" in form or "coated" in form
    )
    is_gel_sku = bool(catalog_tokens & GEL_TOKENS)
    is_gargle_sku = bool(catalog_tokens & GARGLE_TOKENS)

    if is_tablet_sku:
        if evidence_tokens & TABLET_TOKENS:
            boost += 12.0
        if evidence_tokens & (GEL_TOKENS | GARGLE_TOKENS):
            boost -= 12.0

    if is_gel_sku:
        if evidence_tokens & GEL_TOKENS:
            boost += 12.0
        if evidence_tokens & TABLET_TOKENS:
            boost -= 12.0

    if is_gargle_sku:
        if evidence_tokens & GARGLE_TOKENS:
            boost += 12.0
        if evidence_tokens & TABLET_TOKENS:
            boost -= 12.0

    # Doz ipucu: OCR'daki sayilar dosage ile kesisiyorsa hafif boost.
    evidence_numbers = {
        token
        for token in evidence_tokens
        if any(char.isdigit() for char in token)
    }
    dosage_numbers = {
        token
        for token in _token_set(dosage)
        if any(char.isdigit() for char in token)
    }
    if evidence_numbers and dosage_numbers:
        if evidence_numbers & dosage_numbers:
            boost += 5.0

    return boost


def _brand_key(medicine: dict[str, str]) -> str:
    brand = normalize_text(medicine.get("brand_name", "") or "")
    if brand:
        return brand
    return normalize_text(medicine.get("medicine_name", "") or "")


def disambiguate_brand_family_matches(
    ranked_matches: list[MatchRecord],
    *,
    evidence_texts: list[str],
    all_medicines: list[dict[str, str]],
    score_epsilon: float = SCORE_EPSILON,
) -> list[MatchRecord]:
    """
    Ayni marka ailesinde RapidFuzz beraberligini OCR kaniti ile cozer.

    ranked_matches icinde olmasa bile ayni brand_name altindaki
    yakin skorlu SKU'lari yeniden degerlendirir.
    """
    if not ranked_matches:
        return ranked_matches

    top_medicine, top_score, top_ocr = ranked_matches[0]
    brand = _brand_key(top_medicine)
    if not brand:
        return ranked_matches

    evidence = join_evidence_text(evidence_texts)
    query_texts = [
        text.strip()
        for text in evidence_texts
        if text and text.strip()
    ]
    if not query_texts and top_ocr:
        query_texts = [top_ocr]

    family_records: list[MatchRecord] = []
    seen_ids: set[str] = set()

    for medicine in all_medicines:
        if _brand_key(medicine) != brand:
            continue

        medicine_id = medicine.get(
            "medicine_id",
            medicine.get("medicine_name", ""),
        )
        if medicine_id in seen_ids:
            continue

        best_score = 0.0
        best_text = top_ocr or (query_texts[0] if query_texts else "")
        for text in query_texts:
            score, name = calculate_medicine_score(
                query_text=text,
                medicine=medicine,
            )
            if name is None:
                continue
            if score > best_score:
                best_score = score
                best_text = text

        if best_score < top_score - score_epsilon:
            continue

        seen_ids.add(str(medicine_id))
        family_records.append((medicine, best_score, best_text))

    if len(family_records) <= 1:
        return ranked_matches

    def sort_key(record: MatchRecord) -> tuple[float, float, int, int]:
        medicine, score, _ocr = record
        boost = evidence_alignment_boost(medicine, evidence)
        return (
            score + boost,
            boost,
            1 if is_base_sku(medicine) else 0,
            # Son care: kisa isim (uzun varyant varsayilan kazanan olmasin)
            -len(medicine.get("medicine_name", "") or ""),
        )

    family_sorted = sorted(family_records, key=sort_key, reverse=True)

    family_ids = {
        record[0].get(
            "medicine_id",
            record[0].get("medicine_name", ""),
        )
        for record in family_sorted
    }
    remainder = [
        record
        for record in ranked_matches
        if record[0].get(
            "medicine_id",
            record[0].get("medicine_name", ""),
        )
        not in family_ids
    ]
    return family_sorted + remainder
