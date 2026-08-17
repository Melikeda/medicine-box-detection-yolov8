"""medicines.csv quality-control tests."""

from __future__ import annotations

from pathlib import Path

from scripts.validate_medicines_csv import validate_csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MEDICINES_CSV = PROJECT_ROOT / "data/database/medicines.csv"


def test_medicines_csv_structure_and_minimum_size() -> None:
    errors, stats = validate_csv(MEDICINES_CSV)
    assert not errors, errors
    assert stats["rows"] >= 900
    assert stats["duplicate_ids"] == 0


def test_medicines_csv_placeholder_rate_acceptable() -> None:
    _, stats = validate_csv(MEDICINES_CSV)
    total_fields = stats["rows"] * 3
    placeholder_ratio = stats["placeholder_fields"] / total_fields
    assert placeholder_ratio < 0.15


def test_medicine_barcodes_csv_maps_to_catalog() -> None:
    from src.database.csv_reader import load_medicine_barcodes, load_medicines

    barcodes_path = PROJECT_ROOT / "data/database/medicine_barcodes.csv"
    medicines = load_medicines(MEDICINES_CSV)
    known_ids = {row["medicine_id"] for row in medicines}
    barcodes = load_medicine_barcodes(barcodes_path)
    assert len(barcodes) >= 1000
    mapped_ids = {row["medicine_id"] for row in barcodes}
    assert mapped_ids <= known_ids
    codes = [row["barcode"] for row in barcodes]
    assert len(codes) == len(set(codes))
