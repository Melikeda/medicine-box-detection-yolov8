"""TİTCK SKRS barkodlarını medicine_barcodes.csv dosyasına yazar.

Mevcut medicines.csv satırlarını değiştirmez; yalnızca barkod eşlemesi üretir.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.titck.medicine_mapper import assign_skrs_barcodes, normalize_skrs_barcode
from scripts.titck.skrs_client import DEFAULT_OUTPUT_DIR, load_skrs_dataframe, resolve_xlsx_path
from src.barcode.normalize import is_plausible_barcode, normalize_barcode

BARCODE_FIELDS = ["barcode", "medicine_id"]
INDEX_FIELDS = ["barcode", "ilac_adi", "atc_kodu", "atc_adi", "durumu"]
DEFAULT_INDEX_CSV = PROJECT_ROOT / "data/database/titck/skrs_barcode_index.csv"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_barcode_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=BARCODE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_skrs_index(path: Path, frame) -> int:
    """Tüm SKRS barkodlarını hızlı yedek arama CSV'sine yazar."""
    by_code: dict[str, dict[str, str]] = {}
    if "barkod" not in frame.columns:
        return 0
    for _, row in frame.iterrows():
        barcode = normalize_barcode(normalize_skrs_barcode(row.get("barkod")))
        if not is_plausible_barcode(barcode):
            continue
        ilac_adi = str(row.get("ilac_adi") or "").strip()
        if not ilac_adi:
            continue
        durumu = str(row.get("durumu") or "").strip().upper()
        payload = {
            "barcode": barcode,
            "ilac_adi": ilac_adi,
            "atc_kodu": str(row.get("atc_kodu") or "").strip(),
            "atc_adi": str(row.get("atc_adi") or "").strip(),
            "durumu": durumu,
        }
        previous = by_code.get(barcode)
        if previous is None or (
            durumu == "AKTIF" and previous.get("durumu") != "AKTIF"
        ):
            by_code[barcode] = payload

    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [by_code[key] for key in sorted(by_code)]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=INDEX_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Attach TİTCK SKRS barcodes to the medicine catalog",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("data/database/medicines.csv"),
        help="Existing medicines.csv (not modified)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/database/medicine_barcodes.csv"),
        help="Output barcode mapping CSV",
    )
    parser.add_argument(
        "--xlsx",
        type=Path,
        default=None,
        help="Local SKRS XLSX (default: download/use cache)",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Do not download SKRS if cache missing",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=55.0,
        help="Minimum TİTCK name score to attach a barcode",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print summary without writing CSV",
    )
    args = parser.parse_args()

    xlsx_path = resolve_xlsx_path(
        xlsx_path=args.xlsx,
        output_dir=DEFAULT_OUTPUT_DIR,
        download_if_missing=not args.no_download,
    )
    frame = load_skrs_dataframe(xlsx_path)
    medicines = read_csv_rows(args.csv)
    rows = assign_skrs_barcodes(
        medicines,
        frame,
        min_score=args.min_score,
    )

    medicine_ids = {row["medicine_id"] for row in rows}
    print(f"SKRS dosyasi: {xlsx_path}")
    print(f"Katalog ilac: {len(medicines)}")
    print(f"Eslesen barkod: {len(rows)}")
    print(f"Barkodu olan ilac: {len(medicine_ids)}")

    if args.dry_run:
        print("Dry-run: dosya yazilmadi.")
        return

    write_barcode_rows(args.out, rows)
    print(f"Yazildi: {args.out}")
    index_count = write_skrs_index(DEFAULT_INDEX_CSV, frame)
    print(f"SKRS indeks: {index_count} barkod -> {DEFAULT_INDEX_CSV}")


if __name__ == "__main__":
    main()
