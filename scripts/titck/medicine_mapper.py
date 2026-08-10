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
    "M02": "Kas ve Eklem",
    "M03": "Kas Gevşetici",
    "R01": "Soğuk Algınlığı",
    "R03": "Solunum",
    "R05": "Soğuk Algınlığı",
    "R06": "Alerji",
    "J01": "Antibiyotik",
    "J02": "Antibiyotik",
    "P01": "Antibiyotik",
    "A02": "Mide",
    "A03": "Mide",
    "A04": "Mide",
    "A06": "Mide",
    "A07": "Mide",
    "G04": "Mide İlacı",
    "A11": "Vitamin ve Mineral",
    "A12": "Vitamin ve Mineral",
    "B01": "Kardiyoloji",
    "B03": "Vitamin ve Mineral",
    "C01": "Kardiyoloji",
    "C03": "Kardiyoloji",
    "C07": "Kardiyoloji",
    "C08": "Kardiyoloji",
    "C09": "Kardiyoloji",
    "C10": "Kardiyoloji",
    "A10": "Diyabet",
    "H03": "Endokrin",
    "N03": "Nöroloji",
    "N05": "Nöroloji",
    "N06": "Nöroloji",
    "D01": "Dermatoloji",
    "D07": "Dermatoloji",
    "S01": "Göz",
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


# Türkiye’de sık görülen / yüksek hacimli markalar (İEİS kutu lideri
# kategorileri + eczane OTC rafları). Limit = SKRS’ten alınacak max varyant.
EXPANSION_BRAND_QUERIES: list[tuple[str, str, int]] = [
    # Ağrı kesici / ateş (Ipsos: hanelerin ~%80’i)
    ("Parol", "Ağrı Kesici", 12),
    ("Calpol", "Ağrı Kesici", 8),
    ("Panadol", "Ağrı Kesici", 10),
    ("Nurofen", "Ağrı Kesici", 6),
    ("Minoset", "Ağrı Kesici", 5),
    ("Majezik", "Ağrı Kesici", 6),
    ("Apranax", "Ağrı Kesici", 6),
    ("Arveles", "Ağrı Kesici", 5),
    ("Dolorex", "Ağrı Kesici", 5),
    ("Tylol", "Ağrı Kesici", 6),
    ("Brufen", "Ağrı Kesici", 6),
    ("Nimes", "Ağrı Kesici", 5),
    ("Mesulid", "Ağrı Kesici", 4),
    ("Minol", "Ağrı Kesici", 4),
    ("Vermidon", "Ağrı Kesici", 4),
    ("Deflamax", "Ağrı Kesici", 4),
    ("Coraspin", "Ağrı Kesici", 5),
    ("Aspirin", "Ağrı Kesici", 6),
    ("Upsarin", "Ağrı Kesici", 4),
    ("Geralgine", "Ağrı Kesici", 4),
    ("Contramal", "Ağrı Kesici", 4),
    ("Zaldiar", "Ağrı Kesici", 3),
    ("Advil", "Ağrı Kesici", 4),
    ("Moment", "Ağrı Kesici", 3),
    ("Katadolon", "Ağrı Kesici", 3),
    ("Prolix", "Ağrı Kesici", 3),
    ("Naprosyn", "Ağrı Kesici", 4),
    ("Tilcotil", "Ağrı Kesici", 3),
    ("Catafast", "Ağrı Kesici", 4),
    ("Ponstan", "Ağrı Kesici", 3),
    ("Algifen", "Ağrı Kesici", 3),
    ("Novalgine", "Ağrı Kesici", 3),
    ("Peditus", "Ağrı Kesici", 3),
    ("Tempra", "Ağrı Kesici", 4),
    ("Calprofen", "Ağrı Kesici", 3),
    # Antiromatizmal / kas-eklem (İEİS kutu lideri)
    ("Voltaren", "Kas ve Eklem", 8),
    ("Cataflam", "Kas ve Eklem", 5),
    ("Etol", "Kas ve Eklem", 5),
    ("Diclomec", "Kas ve Eklem", 5),
    ("Dicloflam", "Kas ve Eklem", 4),
    ("Flexadol", "Kas ve Eklem", 4),
    ("Mobilat", "Kas ve Eklem", 4),
    ("Parafon", "Kas-İskelet", 4),
    ("Muscoflex", "Kas Gevşetici", 5),
    ("Mydocalm", "Kas Gevşetici", 5),
    ("Draxol", "Kas Gevşetici", 3),
    ("Thiocolchicoside", "Kas Gevşetici", 3),
    ("Lioxan", "Kas Gevşetici", 3),
    ("Miyorel", "Kas Gevşetici", 3),
    ("Flector", "Kas ve Eklem", 4),
    ("Fastum", "Kas ve Eklem", 3),
    ("Deep Heat", "Kas ve Eklem", 2),
    ("Rheumon", "Kas ve Eklem", 3),
    ("Melox", "Kas ve Eklem", 4),
    ("Mobic", "Kas ve Eklem", 3),
    ("Exen", "Kas ve Eklem", 3),
    ("Celebrex", "Kas ve Eklem", 3),
    # Soğuk algınlığı / öksürük
    ("A-Ferin", "Soğuk Algınlığı", 8),
    ("Gripin", "Soğuk Algınlığı", 6),
    ("Theraflu", "Soğuk Algınlığı", 5),
    ("Ibucold", "Soğuk Algınlığı", 5),
    ("Coldaway", "Soğuk Algınlığı", 4),
    ("Sinutab", "Soğuk Algınlığı", 4),
    ("Benical", "Soğuk Algınlığı", 4),
    ("Iburamin", "Soğuk Algınlığı", 4),
    ("Sudafed", "Soğuk Algınlığı", 5),
    ("Otrivin", "Soğuk Algınlığı", 5),
    ("Actifed", "Soğuk Algınlığı", 4),
    ("Ilvico", "Soğuk Algınlığı", 3),
    ("Decolgen", "Soğuk Algınlığı", 3),
    ("Rhinostop", "Soğuk Algınlığı", 3),
    ("Nasovin", "Soğuk Algınlığı", 3),
    ("Avamys", "Soğuk Algınlığı", 3),
    ("Nasonex", "Soğuk Algınlığı", 3),
    ("Mucosolvan", "Öksürük İlacı", 5),
    ("Bisolvon", "Öksürük İlacı", 4),
    ("Levopront", "Öksürük İlacı", 4),
    ("Vicks", "Öksürük İlacı", 4),
    ("Prospan", "Öksürük İlacı", 3),
    ("Sinecod", "Öksürük İlacı", 3),
    ("Bronchicum", "Öksürük İlacı", 3),
    ("Expectus", "Öksürük İlacı", 3),
    ("Oksolin", "Öksürük İlacı", 2),
    # Antibiyotik
    ("Augmentin", "Antibiyotik", 8),
    ("Amoklavin", "Antibiyotik", 6),
    ("Klamoks", "Antibiyotik", 5),
    ("Klavunat", "Antibiyotik", 5),
    ("Biteral", "Antibiyotik", 4),
    ("Cefaks", "Antibiyotik", 5),
    ("Sipro", "Antibiyotik", 4),
    ("Cipro", "Antibiyotik", 5),
    ("Klaacid", "Antibiyotik", 5),
    ("Azitro", "Antibiyotik", 5),
    ("Zitrotek", "Antibiyotik", 4),
    ("Duocid", "Antibiyotik", 4),
    ("Flagyl", "Antibiyotik", 4),
    ("Ornidazole", "Antibiyotik", 3),
    ("Sef", "Antibiyotik", 4),
    ("Cefzil", "Antibiyotik", 3),
    ("Zinnat", "Antibiyotik", 4),
    ("Rocephin", "Antibiyotik", 3),
    ("Suprax", "Antibiyotik", 3),
    ("Monuril", "Antibiyotik", 3),
    ("Fucidin", "Antibiyotik", 4),
    ("Bactrim", "Antibiyotik", 3),
    ("Dalacin", "Antibiyotik", 3),
    ("Tavanic", "Antibiyotik", 3),
    ("Avelox", "Antibiyotik", 3),
    # Mide / sindirim
    ("Omesek", "Mide", 5),
    ("Lansor", "Mide", 5),
    ("Pantpas", "Mide", 5),
    ("Nexium", "Mide", 5),
    ("Controloc", "Mide", 4),
    ("Panthec", "Mide", 4),
    ("Losec", "Mide", 4),
    ("Rennie", "Mide", 3),
    ("Gaviscon", "Mide", 4),
    ("Talcid", "Mide", 3),
    ("Buscopan", "Mide", 5),
    ("Maalox", "Mide", 3),
    ("Spazmol", "Mide", 3),
    ("Motilium", "Mide", 4),
    ("Metpamid", "Mide", 3),
    ("Famodin", "Mide", 3),
    ("Ranitab", "Mide", 3),
    ("Ulcuran", "Mide", 3),
    ("Pariet", "Mide", 3),
    ("Loperamide", "Mide", 3),
    ("Imodium", "Mide", 3),
    ("Smecta", "Mide", 3),
    ("Enterogermina", "Mide", 3),
    ("Nexium Mups", "Mide", 2),
    ("Refluxon", "Mide", 2),
    # Vitamin / mineral / demir
    ("Berocca", "Vitamin ve Mineral", 4),
    ("Redoxon", "Vitamin ve Mineral", 5),
    ("Pharmaton", "Vitamin ve Mineral", 4),
    ("Ferrum", "Vitamin ve Mineral", 6),
    ("Ferro Sanol", "Vitamin ve Mineral", 5),
    ("Supradyn", "Vitamin ve Mineral", 5),
    ("Elevit", "Vitamin ve Mineral", 4),
    ("Magnerot", "Vitamin ve Mineral", 3),
    ("Magne B6", "Vitamin ve Mineral", 4),
    ("Calcimax", "Vitamin ve Mineral", 3),
    ("Devit", "Vitamin ve Mineral", 4),
    ("Vitamin D3", "Vitamin ve Mineral", 3),
    ("Solaray", "Vitamin ve Mineral", 2),
    ("Centrum", "Vitamin ve Mineral", 4),
    ("Becozym", "Vitamin ve Mineral", 3),
    ("Apikobal", "Vitamin ve Mineral", 3),
    ("Neurobion", "Vitamin ve Mineral", 3),
    ("Milgamma", "Vitamin ve Mineral", 3),
    ("Maltofer", "Vitamin ve Mineral", 4),
    ("Endofer", "Vitamin ve Mineral", 3),
    ("Ferrosanol", "Vitamin ve Mineral", 3),
    ("Folbiol", "Vitamin ve Mineral", 3),
    ("Jectofer", "Vitamin ve Mineral", 2),
    # Solunum / astım
    ("Ventolin", "Solunum", 5),
    ("Singulair", "Solunum", 4),
    ("Pulmicort", "Solunum", 4),
    ("Symbicort", "Solunum", 4),
    ("Seretide", "Solunum", 3),
    ("Spiriva", "Solunum", 3),
    ("Budecort", "Solunum", 3),
    ("Foradil", "Solunum", 3),
    ("Atrovent", "Solunum", 3),
    ("Aerius", "Alerji", 4),
    ("Claritine", "Alerji", 4),
    ("Zyrtec", "Alerji", 4),
    ("Xyzal", "Alerji", 4),
    ("Allegra", "Alerji", 3),
    ("Kestine", "Alerji", 3),
    ("Rupafin", "Alerji", 3),
    ("Allerset", "Alerji", 3),
    # Kardiyoloji
    ("Concor", "Kardiyoloji", 5),
    ("Beloc", "Kardiyoloji", 4),
    ("Ator", "Kardiyoloji", 5),
    ("Crestor", "Kardiyoloji", 4),
    ("Lipitor", "Kardiyoloji", 3),
    ("Plavix", "Kardiyoloji", 4),
    ("Karum", "Kardiyoloji", 3),
    ("Coumadin", "Kardiyoloji", 3),
    ("Cordarone", "Kardiyoloji", 3),
    ("Coveram", "Kardiyoloji", 3),
    ("Coversyl", "Kardiyoloji", 3),
    ("Tritace", "Kardiyoloji", 3),
    ("Delix", "Kardiyoloji", 3),
    ("Norvasc", "Kardiyoloji", 4),
    ("Cardura", "Kardiyoloji", 3),
    ("Dilatrend", "Kardiyoloji", 3),
    ("Lasix", "Kardiyoloji", 3),
    ("Aldactone", "Kardiyoloji", 3),
    ("Isordil", "Kardiyoloji", 3),
    ("Imdur", "Kardiyoloji", 3),
    # Diyabet / endokrin
    ("Glucophage", "Diyabet", 5),
    ("Dianben", "Diyabet", 3),
    ("Glucofage", "Diyabet", 3),
    ("Diamicron", "Diyabet", 4),
    ("Amaryl", "Diyabet", 3),
    ("Januvia", "Diyabet", 3),
    ("Galvus", "Diyabet", 3),
    ("Actos", "Diyabet", 3),
    ("Lantus", "Diyabet", 3),
    ("NovoRapid", "Diyabet", 3),
    ("Euthyrox", "Endokrin", 4),
    ("Levotiron", "Endokrin", 4),
    ("Thyro-4", "Endokrin", 2),
    # Nöroloji / psikiyatri (sık reçete)
    ("Desirel", "Nöroloji", 3),
    ("Cipralex", "Nöroloji", 4),
    ("Lustral", "Nöroloji", 3),
    ("Prozac", "Nöroloji", 3),
    ("Paxil", "Nöroloji", 3),
    ("Xanax", "Nöroloji", 3),
    ("Stilnox", "Nöroloji", 3),
    ("Depakin", "Nöroloji", 4),
    ("Tegretol", "Nöroloji", 3),
    ("Keppra", "Nöroloji", 3),
    ("Neurontin", "Nöroloji", 3),
    ("Lyrica", "Nöroloji", 4),
    # Dermatoloji / genel
    ("Bepanthen", "Dermatoloji", 5),
    ("Bepanthol", "Dermatoloji", 3),
    ("Locacid", "Dermatoloji", 3),
    ("Differin", "Dermatoloji", 3),
    ("Betnovate", "Dermatoloji", 3),
    ("Advantan", "Dermatoloji", 3),
    ("Elidel", "Dermatoloji", 2),
    ("Canesten", "Dermatoloji", 3),
    ("Lamisil", "Dermatoloji", 3),
    ("Nizoral", "Dermatoloji", 3),
    ("Thiogel", "Dermatoloji", 2),
    ("Madecassol", "Dermatoloji", 3),
    ("Sudocrem", "Dermatoloji", 2),
    # Göz / diğer sık reçete
    ("Refresh", "Göz", 3),
    ("Tears Naturale", "Göz", 2),
    ("Tobradex", "Göz", 3),
    ("Vigamox", "Göz", 2),
    ("Xalatan", "Göz", 2),
    ("Allergodil", "Göz", 2),
    ("Dexamet", "Genel", 2),
    ("Prednol", "Genel", 3),
    ("Cortef", "Genel", 2),
    ("Ultralan", "Dermatoloji", 2),
    # Ek bilinen Türk markaları
    ("Majezik Duo", "Ağrı Kesici", 2),
    ("Dolorex Plus", "Ağrı Kesici", 2),
    ("Parol Plus", "Ağrı Kesici", 3),
    ("Minoset Plus", "Ağrı Kesici", 2),
    ("Theraflu Forte", "Soğuk Algınlığı", 2),
    ("Coldaway C", "Soğuk Algınlığı", 2),
    ("Amoklavin BID", "Antibiyotik", 2),
    ("Augmentin BID", "Antibiyotik", 2),
    ("Pantpas IV", "Mide", 2),
    ("Nexium IV", "Mide", 2),
]

# Yüksek hacimli ATC gruplarından ek SKRS ürünleri (marka listesini tamamlar)
POPULAR_ATC_EXPANSION: list[tuple[str, str, int]] = [
    ("N02", "Ağrı Kesici", 80),
    ("M01", "Kas ve Eklem", 70),
    ("M03", "Kas Gevşetici", 40),
    ("R05", "Soğuk Algınlığı", 50),
    ("R01", "Soğuk Algınlığı", 30),
    ("R06", "Alerji", 40),
    ("R03", "Solunum", 40),
    ("J01", "Antibiyotik", 100),
    ("A02", "Mide", 70),
    ("A03", "Mide", 40),
    ("A11", "Vitamin ve Mineral", 50),
    ("A12", "Vitamin ve Mineral", 30),
    ("B03", "Vitamin ve Mineral", 30),
    ("C07", "Kardiyoloji", 40),
    ("C09", "Kardiyoloji", 40),
    ("C10", "Kardiyoloji", 40),
    ("A10", "Diyabet", 40),
    ("H03", "Endokrin", 20),
    ("N06", "Nöroloji", 30),
    ("D07", "Dermatoloji", 25),
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


def _append_titck_candidate(
    *,
    rows: list[dict[str, str]],
    used_names: set[str],
    next_id: int,
    titck_row: pd.Series,
    category_hint: str,
) -> int:
    candidate = build_row_from_titck(
        medicine_id=f"MED{next_id:03d}",
        ilac_adi=str(titck_row["ilac_adi"]),
        atc_kodu=str(titck_row["atc_kodu"]),
        atc_adi=str(titck_row["atc_adi"]),
        category_hint=category_hint,
    )
    key = normalize_match_text(candidate["medicine_name"])
    if key in used_names:
        return next_id
    rows.append(candidate)
    used_names.add(key)
    return next_id + 1


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
            before = next_id
            next_id = _append_titck_candidate(
                rows=rows,
                used_names=used_names,
                next_id=next_id,
                titck_row=titck_row,
                category_hint=category_hint,
            )
            if next_id > before:
                added += 1
            if added >= limit:
                break

    # Marka listesinden sonra yüksek hacimli ATC gruplarından tamamla
    for atc_prefix, category_hint, limit in POPULAR_ATC_EXPANSION:
        group = active[
            active["atc_kodu"].astype(str).str.upper().str.startswith(atc_prefix)
        ]
        added = 0
        for _, titck_row in group.iterrows():
            atc_kodu = str(titck_row["atc_kodu"])
            if _is_excluded_expansion_atc(atc_kodu):
                continue
            before = next_id
            next_id = _append_titck_candidate(
                rows=rows,
                used_names=used_names,
                next_id=next_id,
                titck_row=titck_row,
                category_hint=category_hint,
            )
            if next_id > before:
                added += 1
            if added >= limit:
                break

    return rows
