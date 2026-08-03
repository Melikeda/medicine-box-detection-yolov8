"""TİTCK SKRS listesini indirir (data/database/titck/skrs_latest.xlsx)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.titck.skrs_client import (
    DEFAULT_OUTPUT_DIR,
    download_skrs_xlsx,
    load_skrs_dataframe,
    write_manifest,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download latest TİTCK SKRS XLSX to data/database/titck/",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Download directory",
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    xlsx_path = output_dir / "skrs_latest.xlsx"
    manifest_path = output_dir / "skrs_manifest.json"

    info = download_skrs_xlsx(xlsx_path)
    frame = load_skrs_dataframe(xlsx_path)
    write_manifest(manifest_path, info, row_count=len(frame), xlsx_path=xlsx_path)

    print(f"TİTCK SKRS indirildi: {xlsx_path}")
    print(f"Aktif urun satiri: {len(frame)}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
