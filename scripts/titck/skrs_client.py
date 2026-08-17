"""
Downloads and parses the TITCK SKRS e-prescription medicine list.
"""

from __future__ import annotations

import re
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

TITCK_SKRS_PAGE_URL = "https://www.titck.gov.tr/dinamikmodul/43"
DEFAULT_OUTPUT_DIR = Path("data/database/titck")

SKRS_COLUMNS = [
    "ilac_adi",
    "barkod",
    "atc_kodu",
    "atc_adi",
    "firma",
    "recete_turu",
    "durumu",
    "aciklama",
    "temel_ilac",
    "cocuk_temel",
    "yenidogan_temel",
    "tarih",
]


@dataclass(frozen=True)
class SkrsDownloadInfo:
    title: str
    url: str
    file_name: str


def discover_latest_skrs_xlsx(
    page_url: str = TITCK_SKRS_PAGE_URL,
    timeout: int = 30,
) -> SkrsDownloadInfo:
    """Finds the latest XLSX link on the TITCK SKRS page."""
    response = requests.get(page_url, timeout=timeout)
    response.raise_for_status()
    html = response.text

    matches = re.findall(
        r'href="(https://titck\.gov\.tr/storage/Archive/\d+/dynamicModulesAttachment/[^"]+\.xlsx)"',
        html,
        flags=re.IGNORECASE,
    )
    if not matches:
        raise RuntimeError("TİTCK SKRS XLSX bağlantısı bulunamadi.")

    url = matches[0]
    file_name = url.rsplit("/", maxsplit=1)[-1]
    title = file_name
    return SkrsDownloadInfo(title=title, url=url, file_name=file_name)


def download_skrs_xlsx(
    output_path: Path,
    *,
    page_url: str = TITCK_SKRS_PAGE_URL,
    timeout: int = 60,
) -> SkrsDownloadInfo:
    info = discover_latest_skrs_xlsx(page_url=page_url, timeout=timeout)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(info.url, timeout=timeout, stream=True) as response:
        response.raise_for_status()
        output_path.write_bytes(response.content)

    return info


def _barcode_cell_to_text(value: object) -> str:
    """Converts Excel floats, .0 values, and scientific notation to a digit string."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(value, bool):
        return ""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return ""
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none"}:
        return ""
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    scientific = re.fullmatch(
        r"\d+(?:\.\d+)?[eE][+-]?\d+",
        text,
    )
    if scientific:
        try:
            as_int = int(float(text))
            if as_int > 0:
                return str(as_int)
        except (TypeError, ValueError, OverflowError):
            return text
    return text


def load_skrs_dataframe(xlsx_path: Path) -> pd.DataFrame:
    """Loads the active-products list with normalized columns."""
    raw = pd.read_excel(xlsx_path, sheet_name=0, skiprows=2)
    raw.columns = SKRS_COLUMNS[: len(raw.columns)]
    frame = raw.copy()
    frame["ilac_adi"] = frame["ilac_adi"].astype(str).str.strip()
    frame["atc_kodu"] = frame["atc_kodu"].astype(str).str.strip()
    frame["atc_adi"] = frame["atc_adi"].astype(str).str.strip()
    frame["durumu"] = frame["durumu"].astype(str).str.strip()
    if "barkod" in frame.columns:
        frame["barkod"] = frame["barkod"].map(_barcode_cell_to_text)
    frame = frame[frame["ilac_adi"].str.len() > 0]
    frame = frame[~frame["ilac_adi"].str.lower().eq("nan")]
    return frame.reset_index(drop=True)


def write_manifest(
    manifest_path: Path,
    info: SkrsDownloadInfo,
    *,
    row_count: int,
    xlsx_path: Path,
) -> None:
    payload: dict[str, Any] = {
        "source": "TİTCK SKRS E-Reçete İlaç ve Diğer Farmasötik Ürünler Listesi",
        "source_page": TITCK_SKRS_PAGE_URL,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "file_name": info.file_name,
        "download_url": info.url,
        "local_path": str(xlsx_path.as_posix()),
        "active_product_rows": row_count,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def resolve_xlsx_path(
    *,
    xlsx_path: Path | None,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    download_if_missing: bool = True,
) -> Path:
    if xlsx_path is not None and xlsx_path.exists():
        return xlsx_path

    candidate = output_dir / "skrs_latest.xlsx"
    if candidate.exists():
        return candidate

    if not download_if_missing:
        raise FileNotFoundError(
            f"SKRS dosyasi bulunamadi: {candidate}. "
            "Once scripts/fetch_titck_skrs.py calistirin."
        )

    download_skrs_xlsx(candidate)
    return candidate
