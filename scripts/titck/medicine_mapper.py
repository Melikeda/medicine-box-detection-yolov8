"""TİTCK SKRS kayıtlarını proje CSV şemasına eşler."""

from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd

PLACEHOLDER = "VERIFY_FROM_OFFICIAL_LEAFLET"
PLACEHOLDER_PRODUCT = "VERIFY_FROM_OFFICIAL_PRODUCT"

FORM_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"FILM\s*KAPLI\s*TABLET", re.I), "Film Kaplı Tablet"),
    (re.compile(r"KAPLI\s*TABLET", re.I), "Kaplı Tablet"),
    (re.compile(r"EFERVESAN\s*TABLET", re.I), "Efervesan Tablet"),
    (re.compile(r"CHEWABLE\s*TABLET|ÇIGNENEBILIR\s*TABLET", re.I), "Çiğnenebilir Tablet"),
    (re.compile(r"SURUP|ŞURUP", re.I), "Şurup"),
    (re.compile(r"SASE|SAŞE", re.I), "Saşe"),
    (re.compile(r"KAPSUL|KAPSÜL", re.I), "Kapsül"),
    (re.compile(r"TABLET", re.I), "Tablet"),
    (re.compile(r"DAMLA", re.I), "Damla"),
    (re.compile(r"SUSPANSIYON", re.I), "Süspansiyon"),
    (re.compile(r"SPRAY", re.I), "Sprey"),
    (re.compile(r"KREM", re.I), "Krem"),
]

ATC_PREFIX_CATEGORY: dict[str, str] = {
    "N02": "Ağrı Kesici",
    "M01": "Kas ve Eklem",
    "M03": "Kas Gevşetici",
    "R05": "Soğuk Algınlığı",
    "R06": "Soğuk Algınlığı",
    "J01": "Antibiyotik",
    "P01": "Antibiyotik",
    "A02": "Mide",
    "A03": "Mide",
    "G04": "Mide İlacı",
    "A11": "Vitamin ve Mineral",
    "A12": "Vitamin ve Mineral",
}


@dataclass(frozen=True)
class TitckMatch:
    ilac_adi: str
    atc_kodu: str
    atc_adi: str
    score: float


def normalize_match_text(value: str) -> str:
    text = value.upper().strip()
    text = text.replace("İ", "I").replace("Ş", "S").replace("Ç", "C")
    text = text.replace("Ö", "O").replace("Ü", "U").replace("Ğ", "G")
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(value: str) -> list[str]:
    tokens = normalize_match_text(value).split()
    stop = {"MG", "ML", "MCG", "IU", "GR", "G", "AND", "TABLET", "FILM", "KAPLI"}
    return [token for token in tokens if token not in stop and len(token) > 1]


def parse_form(ilac_adi: str) -> str | None:
    for pattern, label in FORM_PATTERNS:
        if pattern.search(ilac_adi):
            return label
    return None


def parse_dosage(ilac_adi: str) -> str | None:
    parts = re.findall(
        r"(\d+(?:[.,]\d+)?\s*(?:MG|MCG|ML|G|IU)(?:\s*/\s*\d+(?:[.,]\d+)?\s*(?:MG|MCG|ML|G|IU))*)",
        ilac_adi,
        flags=re.IGNORECASE,
    )
    if not parts:
        return None
    cleaned = [re.sub(r"\s+", " ", part.replace(",", ".").upper()) for part in parts[:3]]
    return " / ".join(cleaned)


def category_from_atc(atc_kodu: str, fallback: str | None = None) -> str | None:
    prefix = atc_kodu[:3].upper() if atc_kodu else ""
    return ATC_PREFIX_CATEGORY.get(prefix, fallback)


def score_titck_row(
    medicine_name: str,
    brand_name: str,
    ilac_adi: str,
) -> float:
    name_norm = normalize_match_text(medicine_name)
    brand_norm = normalize_match_text(brand_name)
    row_norm = normalize_match_text(ilac_adi)

    if name_norm and name_norm in row_norm:
        score = 100.0
    else:
        medicine_tokens = tokenize(medicine_name)
        brand_tokens = tokenize(brand_name)
        wanted = medicine_tokens or brand_tokens
        if not wanted:
            return 0.0
        hits = sum(1 for token in wanted if token in row_norm.split())
        score = (hits / len(wanted)) * 80.0

    if brand_norm and brand_norm.split()[0] in row_norm.split():
        score += 10.0

    variant_tokens = [
        "PLUS",
        "FORTE",
        "SINUS",
        "ZERO",
        "MIGRA",
        "RETARD",
        "SR",
        "EMULGEL",
        "BEBE",
        "COLD",
        "FLU",
        "DUO",
        "ES",
    ]
    for token in variant_tokens:
        if token in row_norm.split() and token not in name_norm.split():
            score -= 18.0

    score -= min(len(row_norm) / 200.0, 10.0)
    return score


def find_best_titck_match(
    frame: pd.DataFrame,
    *,
    medicine_name: str,
    brand_name: str,
    min_score: float = 55.0,
) -> TitckMatch | None:
    active = frame[frame["durumu"].str.upper().eq("AKTIF")]
    best: TitckMatch | None = None

    for _, row in active.iterrows():
        ilac_adi = str(row["ilac_adi"])
        score = score_titck_row(medicine_name, brand_name, ilac_adi)
        if score < min_score:
            continue
        candidate = TitckMatch(
            ilac_adi=ilac_adi,
            atc_kodu=str(row["atc_kodu"]),
            atc_adi=str(row["atc_adi"]),
            score=score,
        )
        if best is None or candidate.score > best.score:
            best = candidate

    return best


def enrich_row_from_titck(
    row: dict[str, str],
    frame: pd.DataFrame,
) -> dict[str, str]:
    match = find_best_titck_match(
        frame,
        medicine_name=row["medicine_name"],
        brand_name=row.get("brand_name", row["medicine_name"]),
    )
    if match is None:
        return row

    updated = dict(row)
    if _is_placeholder(updated.get("active_ingredient")):
        updated["active_ingredient"] = match.atc_adi.title()

    dosage = parse_dosage(match.ilac_adi)
    if dosage and _is_placeholder(updated.get("dosage")):
        updated["dosage"] = dosage

    form = parse_form(match.ilac_adi)
    if form and _is_placeholder(updated.get("form")):
        updated["form"] = form

    category = category_from_atc(match.atc_kodu, updated.get("category"))
    if category and _is_placeholder(updated.get("category")):
        updated["category"] = category

    return updated


def _is_placeholder(value: str | None) -> bool:
    if value is None:
        return True
    stripped = value.strip()
    return not stripped or stripped in {PLACEHOLDER, PLACEHOLDER_PRODUCT}


def build_row_from_titck(
    *,
    medicine_id: str,
    ilac_adi: str,
    atc_kodu: str,
    atc_adi: str,
    category_hint: str | None = None,
) -> dict[str, str]:
    brand = ilac_adi.split()[0]
    return {
        "medicine_id": medicine_id,
        "medicine_name": _display_name_from_titck(ilac_adi),
        "brand_name": brand.title() if brand.isupper() else brand,
        "active_ingredient": atc_adi.title(),
        "dosage": parse_dosage(ilac_adi) or PLACEHOLDER,
        "form": parse_form(ilac_adi) or PLACEHOLDER,
        "category": category_from_atc(atc_kodu, category_hint) or "Genel",
    }


def _display_name_from_titck(ilac_adi: str) -> str:
    """OCR için kısa görünen ad: doz/form öncesindeki bölüm."""
    upper = ilac_adi.upper()
    cut_patterns = [
        r"\s+\d",
        r"\s+FILM",
        r"\s+TABLET",
        r"\s+KAPS",
        r"\s+SURUP",
        r"\s+ŞURUP",
        r"\s+DAMLA",
        r"\s+SPRAY",
    ]
    cut_at = len(upper)
    for pattern in cut_patterns:
        match = re.search(pattern, upper)
        if match:
            cut_at = min(cut_at, match.start())
    short = ilac_adi[:cut_at].strip(" -")
    short = re.sub(r"\s+", " ", short)
    return short.title() if short.isupper() else short


EXPANSION_BRAND_QUERIES: list[tuple[str, str, int]] = [
    ("Parol", "Ağrı Kesici", 10),
    ("Calpol", "Ağrı Kesici", 7),
    ("Panadol", "Ağrı Kesici", 8),
    ("Nurofen", "Ağrı Kesici", 4),
    ("Minoset", "Ağrı Kesici", 3),
    ("Majezik", "Ağrı Kesici", 4),
    ("Apranax", "Ağrı Kesici", 4),
    ("Arveles", "Ağrı Kesici", 3),
    ("Dolorex", "Ağrı Kesici", 3),
    ("Tylol", "Ağrı Kesici", 4),
    ("Brufen", "Ağrı Kesici", 5),
    ("Nimes", "Ağrı Kesici", 4),
    ("Mesulid", "Ağrı Kesici", 3),
    ("Minol", "Ağrı Kesici", 3),
    ("A-Ferin", "Soğuk Algınlığı", 6),
    ("Gripin", "Soğuk Algınlığı", 5),
    ("Theraflu", "Soğuk Algınlığı", 4),
    ("Ibucold", "Soğuk Algınlığı", 4),
    ("Coldaway", "Soğuk Algınlığı", 3),
    ("Sinutab", "Soğuk Algınlığı", 3),
    ("Benical", "Soğuk Algınlığı", 3),
    ("Augmentin", "Antibiyotik", 5),
    ("Amoklavin", "Antibiyotik", 4),
    ("Klamoks", "Antibiyotik", 3),
    ("Biteral", "Antibiyotik", 3),
    ("Cefaks", "Antibiyotik", 4),
    ("Sipro", "Antibiyotik", 3),
    ("Klavunat", "Antibiyotik", 3),
    ("Voltaren", "Kas ve Eklem", 5),
    ("Parafon", "Kas-İskelet", 3),
    ("Etol", "Kas ve Eklem", 3),
    ("Flexadol", "Kas ve Eklem", 3),
    ("Mydocalm", "Kas Gevşetici", 4),
    ("Omesek", "Mide İlacı", 3),
    ("Lansor", "Mide", 3),
    ("Pantpas", "Mide", 3),
    ("Nexium", "Mide", 3),
    ("Rennie", "Mide", 2),
    ("Gaviscon", "Mide", 2),
    ("Mucosolvan", "Öksürük İlacı", 4),
    ("Bisolvon", "Öksürük İlacı", 3),
    ("Berocca", "Vitamin ve Mineral", 3),
    ("Redoxon", "Vitamin ve Mineral", 3),
    ("Pharmaton", "Vitamin ve Mineral", 3),
    ("Iburamin", "Soğuk Algınlığı", 3),
    ("Deflamax", "Ağrı Kesici", 3),
    ("Coraspin", "Ağrı Kesici", 4),
    ("Aspirin", "Ağrı Kesici", 4),
    ("Cataflam", "Kas ve Eklem", 4),
    ("Mobilat", "Kas ve Eklem", 3),
    ("Vermidon", "Ağrı Kesici", 2),
    ("Talcid", "Mide", 2),
    ("Draxol", "Kas Gevşetici", 2),
    ("Sudafed", "Soğuk Algınlığı", 3),
    ("Otrivin", "Soğuk Algınlığı", 4),
    ("Bepanthen", "Genel", 3),
]

# Tanı / radyoloji / aşı gibi OTC genişletme dışı ATC önekleri
EXCLUDED_EXPANSION_ATC_PREFIXES = (
    "V08",
    "B05",
    "J06",
    "J07",
    "L01",
    "L02",
    "L03",
    "L04",
)


def _brand_matches_ilac(brand_query: str, ilac_adi: str) -> bool:
    query_norm = normalize_match_text(brand_query)
    row_norm = normalize_match_text(ilac_adi)
    tokens = [token for token in query_norm.split() if len(token) > 1]
    if not tokens:
        tokens = query_norm.split()
    return all(token in row_norm for token in tokens)


def _is_excluded_expansion_atc(atc_kodu: str) -> bool:
    code = atc_kodu.upper().strip()
    return any(code.startswith(prefix) for prefix in EXCLUDED_EXPANSION_ATC_PREFIXES)


def discover_expansion_rows(
    frame: pd.DataFrame,
    existing_names: set[str],
    *,
    start_index: int,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    used_names: set[str] = set(existing_names)
    next_id = start_index

    active = frame[frame["durumu"].str.upper().eq("AKTIF")]

    for brand_query, category_hint, limit in EXPANSION_BRAND_QUERIES:
        candidates: list[tuple[float, pd.Series]] = []
        for _, titck_row in active.iterrows():
            ilac_adi = str(titck_row["ilac_adi"])
            atc_kodu = str(titck_row["atc_kodu"])
            if _is_excluded_expansion_atc(atc_kodu):
                continue
            if not _brand_matches_ilac(brand_query, ilac_adi):
                continue
            score = score_titck_row(brand_query, brand_query, ilac_adi)
            if score < 55.0:
                continue
            candidates.append((score, titck_row))

        candidates.sort(key=lambda item: item[0], reverse=True)
        added = 0
        for _, titck_row in candidates:
            candidate = build_row_from_titck(
                medicine_id=f"MED{next_id:03d}",
                ilac_adi=str(titck_row["ilac_adi"]),
                atc_kodu=str(titck_row["atc_kodu"]),
                atc_adi=str(titck_row["atc_adi"]),
                category_hint=category_hint,
            )
            key = normalize_match_text(candidate["medicine_name"])
            if key in used_names:
                continue
            rows.append(candidate)
            used_names.add(key)
            next_id += 1
            added += 1
            if added >= limit:
                break

    return rows
