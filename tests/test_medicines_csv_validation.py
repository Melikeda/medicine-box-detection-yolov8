"""medicines.csv kalite kontrol testleri."""

from __future__ import annotations

from pathlib import Path

from scripts.validate_medicines_csv import validate_csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MEDICINES_CSV = PROJECT_ROOT / "data/database/medicines.csv"


def test_medicines_csv_structure_and_minimum_size() -> None:
    errors, stats = validate_csv(MEDICINES_CSV)
    assert not errors, errors
    assert stats["rows"] >= 130
    assert stats["duplicate_ids"] == 0


def test_medicines_csv_placeholder_rate_acceptable() -> None:
    _, stats = validate_csv(MEDICINES_CSV)
    total_fields = stats["rows"] * 3
    placeholder_ratio = stats["placeholder_fields"] / total_fields
    assert placeholder_ratio < 0.15
