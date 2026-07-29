"""CSV'deki ilaçları SQLite veritabanına aktarır."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.repository import seed_medicines_from_csv
from src.services.config import PipelineConfig


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Seed SQLite medicine database from medicines.csv"
        ),
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="CSV path (default: PipelineConfig.medicines_csv_path)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="SQLite path (default: PipelineConfig.sqlite_path)",
    )
    args = parser.parse_args()

    config = PipelineConfig()
    csv_path = args.csv or config.medicines_csv_path
    db_path = args.db or config.sqlite_path

    count = seed_medicines_from_csv(
        csv_path=csv_path,
        database_path=db_path,
        replace_existing=True,
    )

    print(f"Seed tamamlandi: {count} ilac -> {db_path}")


if __name__ == "__main__":
    main()
