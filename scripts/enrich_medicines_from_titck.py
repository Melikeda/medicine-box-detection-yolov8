"""medicines.csv dosyasını TİTCK SKRS verisiyle zenginlestirir ve genisletir."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.titck.manual_overrides import apply_manual_overrides
from scripts.titck.medicine_mapper import (
    discover_expansion_rows,
    enrich_row_from_titck,
    normalize_match_text,
)
from scripts.titck.popular_manual_rows import append_popular_manual_rows
from scripts.titck.skrs_client import DEFAULT_OUTPUT_DIR, load_skrs_dataframe, resolve_xlsx_path

CSV_FIELDS = [
    "medicine_id",
    "medicine_name",
    "brand_name",
    "active_ingredient",
    "dosage",
    "form",
    "category",
]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def next_medicine_index(rows: list[dict[str, str]]) -> int:
    max_id = 0
    for row in rows:
        raw = row.get("medicine_id", "")
        if raw.startswith("MED") and raw[3:].isdigit():
            max_id = max(max_id, int(raw[3:]))
    return max_id + 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enrich and expand medicines.csv using TİTCK SKRS data",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("data/database/medicines.csv"),
        help="Target medicines CSV",
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
        "--no-expand",
        action="store_true",
        help="Only enrich existing rows; do not append new medicines",
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
    rows = read_csv_rows(args.csv)

    enriched_rows = [
        apply_manual_overrides(enrich_row_from_titck(row, frame)) for row in rows
    ]
    existing_names = {
        normalize_match_text(row["medicine_name"]) for row in enriched_rows
    }

    if not args.no_expand:
        start_index = next_medicine_index(enriched_rows)
        expansion = discover_expansion_rows(
            frame,
            existing_names,
            start_index=start_index,
        )
        enriched_rows.extend(expansion)
        existing_names = {
            normalize_match_text(row["medicine_name"])
            for row in enriched_rows
        }
        start_index = next_medicine_index(enriched_rows)
        popular_rows = append_popular_manual_rows(
            enriched_rows,
            frame,
            start_index=start_index,
        )
        enriched_rows.extend(popular_rows)

    if args.dry_run:
        print(f"Rows total: {len(enriched_rows)}")
        print(f"SKRS source: {xlsx_path}")
        return

    write_csv_rows(args.csv, enriched_rows)
    print(f"Guncellendi: {args.csv} ({len(enriched_rows)} kayit)")


if __name__ == "__main__":
    main()
