"""Yerel analyze pipeline benchmark aracı."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.config import PipelineConfig
from src.services.pipeline_manager import PipelineManager


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark analyze pipeline (YOLO + OCR + matching)",
    )
    parser.add_argument(
        "--image",
        type=Path,
        required=True,
        help="Sample image path",
    )
    parser.add_argument(
        "--mode",
        choices=("fast", "accurate"),
        default="fast",
        help="OCR mode",
    )
    args = parser.parse_args()

    if not args.image.exists():
        raise SystemExit(f"Görüntü bulunamadi: {args.image}")

    config = PipelineConfig(ocr_mode=args.mode)
    manager = PipelineManager.get_instance(config)
    manager.load()

    started = time.perf_counter()
    result = manager.analyze_all(args.image)
    wall_ms = (time.perf_counter() - started) * 1000

    print(f"Mod: {args.mode}")
    print(f"Görüntü: {args.image}")
    print(f"Tespit: {result.detection_count}")
    print(f"Basari: {result.success}")

    if result.timing:
        print(
            "Aşama süreleri (ms): "
            f"YOLO={result.timing.yolo_ms:.0f}, "
            f"OCR={result.timing.ocr_ms:.0f}, "
            f"Matching={result.timing.matching_ms:.0f}, "
            f"Pipeline={result.timing.total_ms:.0f}"
        )

    print(f"Duvar saati (ms): {wall_ms:.0f}")

    for box in result.medicines:
        label = box.medicine_name or box.status
        print(
            f"  Kutu {box.box_index}: {label} "
            f"(skor={box.matching_score:.1f})"
        )


if __name__ == "__main__":
    main()
