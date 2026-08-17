"""TİTCK SKRS barkod yedek araması (CSV eşleşmesi kaçınca)."""

from __future__ import annotations

import csv
import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from src.barcode.normalize import barcode_lookup_keys, is_plausible_barcode, normalize_barcode
from src.services.model_paths import PROJECT_ROOT

logger = logging.getLogger(__name__)

DEFAULT_SKRS_INDEX_CSV = PROJECT_ROOT / "data/database/titck/skrs_barcode_index.csv"
DEFAULT_SKRS_XLSX = PROJECT_ROOT / "data/database/titck/skrs_latest.xlsx"
_DISABLE_ENV = "YOLOCILIN_DISABLE_SKRS_FALLBACK"


@dataclass(frozen=True)
class SkrsBarcodeHit:
    barcode: str
    ilac_adi: str
    atc_kodu: str
    atc_adi: str


def skrs_fallback_disabled() -> bool:
    return os.environ.get(_DISABLE_ENV, "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def resolve_skrs_barcode(
    raw_code: str,
    *,
    index_csv: Path | None = None,
    xlsx_path: Path | None = None,
) -> SkrsBarcodeHit | None:
    """SKRS listesinde barkodu birebir arar. Dosya yoksa None."""
    explicit = index_csv is not None or xlsx_path is not None
    if skrs_fallback_disabled() and not explicit:
        return None

    index = _skrs_index(
        str(index_csv) if index_csv is not None else "",
        str(xlsx_path) if xlsx_path is not None else "",
    )
    if not index:
        return None
    for key in barcode_lookup_keys(raw_code):
        hit = index.get(key)
        if hit is not None:
            return hit
    return None


def medicine_from_skrs_hit(hit: SkrsBarcodeHit) -> dict[str, str]:
    """Katalogda yoksa TİTCK satırından gösterim kaydı üretir."""
    from scripts.titck.medicine_mapper import (
        _display_name_from_titck,
        category_from_atc,
        parse_dosage,
        parse_form,
        tokenize,
    )

    tokens = tokenize(hit.ilac_adi)
    brand = tokens[0].title() if tokens else hit.ilac_adi[:40]
    return {
        "medicine_id": f"SKRS-{hit.barcode}",
        "medicine_name": _display_name_from_titck(hit.ilac_adi),
        "brand_name": brand,
        "active_ingredient": hit.atc_adi.title() if hit.atc_adi else "",
        "dosage": parse_dosage(hit.ilac_adi) or "",
        "form": parse_form(hit.ilac_adi) or "",
        "category": category_from_atc(hit.atc_kodu) or "Genel",
    }


def match_skrs_hit_to_catalog(
    hit: SkrsBarcodeHit,
    medicines: list[dict[str, str]],
    *,
    min_score: float = 55.0,
) -> dict[str, str] | None:
    from scripts.titck.medicine_mapper import score_titck_row

    best: dict[str, str] | None = None
    best_score = 0.0
    for medicine in medicines:
        score = score_titck_row(
            medicine.get("medicine_name", ""),
            medicine.get("brand_name", ""),
            hit.ilac_adi,
        )
        if score > best_score:
            best_score = score
            best = medicine
    if best is None or best_score < min_score:
        return None
    return best


def warmup_skrs_index() -> int:
    """API açılışında SKRS indeksini belleğe alır."""
    if skrs_fallback_disabled():
        return 0
    index = _skrs_index("", "")
    logger.info("SKRS barcode index ready (%s keys)", len(index))
    return len(index)


@lru_cache(maxsize=4)
def _skrs_index(index_csv_key: str, xlsx_key: str) -> dict[str, SkrsBarcodeHit]:
    csv_path = Path(index_csv_key) if index_csv_key else DEFAULT_SKRS_INDEX_CSV
    xlsx_path = Path(xlsx_key) if xlsx_key else DEFAULT_SKRS_XLSX

    if csv_path.is_file():
        return _index_from_csv(csv_path)
    if xlsx_path.is_file():
        return _index_from_xlsx(xlsx_path)
    return {}


def _index_from_csv(path: Path) -> dict[str, SkrsBarcodeHit]:
    index: dict[str, SkrsBarcodeHit] = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            _add_hit(
                index,
                barcode=row.get("barcode") or "",
                ilac_adi=(row.get("ilac_adi") or "").strip(),
                atc_kodu=(row.get("atc_kodu") or "").strip(),
                atc_adi=(row.get("atc_adi") or "").strip(),
                prefer=str(row.get("durumu") or "").strip().upper() == "AKTIF",
            )
    return index


def _index_from_xlsx(path: Path) -> dict[str, SkrsBarcodeHit]:
    from scripts.titck.skrs_client import load_skrs_dataframe

    frame = load_skrs_dataframe(path)
    index: dict[str, SkrsBarcodeHit] = {}
    if "barkod" not in frame.columns:
        return {}

    for _, row in frame.iterrows():
        _add_hit(
            index,
            barcode=str(row.get("barkod") or ""),
            ilac_adi=str(row.get("ilac_adi") or "").strip(),
            atc_kodu=str(row.get("atc_kodu") or "").strip(),
            atc_adi=str(row.get("atc_adi") or "").strip(),
            prefer=str(row.get("durumu") or "").strip().upper() == "AKTIF",
        )
    return index


def _add_hit(
    index: dict[str, SkrsBarcodeHit],
    *,
    barcode: str,
    ilac_adi: str,
    atc_kodu: str,
    atc_adi: str,
    prefer: bool,
) -> None:
    normalized = normalize_barcode(barcode)
    if not is_plausible_barcode(normalized) or not ilac_adi:
        return
    hit = SkrsBarcodeHit(
        barcode=normalized,
        ilac_adi=ilac_adi,
        atc_kodu=atc_kodu,
        atc_adi=atc_adi,
    )
    for key in barcode_lookup_keys(normalized):
        existing = index.get(key)
        if existing is None or prefer:
            index[key] = hit
