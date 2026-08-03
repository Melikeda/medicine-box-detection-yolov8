"""medicines.csv kalite kontrol scripti."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PLACEHOLDERS = {"VERIFY_FROM_OFFICIAL_LEAFLET", "VERIFY_FROM_OFFICIAL_PRODUCT"}
REQUIRED_FIELDS = [
    "medicine_id",
    "medicine_name",
    "brand_name",
    "active_ingredient",
    "dosage",
    "form",
    "category",
]


def validate_csv(path: Path) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    stats = {
        "rows": 0,
        "placeholder_fields": 0,
        "duplicate_ids": 0,
    }

    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    stats["rows"] = len(rows)
    seen_ids: set[str] = set()

    for index, row in enumerate(rows, start=2):
        for field in REQUIRED_FIELDS:
            if field not in row or not str(row[field]).strip():
                errors.append(f"Satir {index}: bos alan -> {field}")

        medicine_id = row.get("medicine_id", "").strip()
        if medicine_id in seen_ids:
            stats["duplicate_ids"] += 1
            errors.append(f"Satir {index}: duplicate medicine_id {medicine_id}")
        seen_ids.add(medicine_id)

        for field in ("active_ingredient", "dosage", "form"):
            if str(row.get(field, "")).strip() in PLACEHOLDERS:
                stats["placeholder_fields"] += 1

    return errors, stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate medicines.csv")
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("data/database/medicines.csv"),
    )
    args = parser.parse_args()

    errors, stats = validate_csv(args.csv)
    print(f"Dosya: {args.csv}")
    print(f"Kayit sayisi: {stats['rows']}")
    print(f"Placeholder alan sayisi: {stats['placeholder_fields']}")

    if errors:
        print("\nHatalar:")
        for error in errors[:20]:
            print(f"- {error}")
        raise SystemExit(1)

    print("CSV dogrulama basarili.")


if __name__ == "__main__":
    main()
