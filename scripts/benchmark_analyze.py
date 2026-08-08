"""Yerel analyze pipeline benchmark aracı."""

from __future__ import annotations

import argparse
import json
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
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional JSON report path",
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

    timing_payload = None
    if result.timing:
        timing_payload = {
            "yolo_ms": round(result.timing.yolo_ms, 1),
            "ocr_ms": round(result.timing.ocr_ms, 1),
            "matching_ms": round(result.timing.matching_ms, 1),
            "total_ms": round(result.timing.total_ms, 1),
        }
        print(
            "Aşama süreleri (ms): "
            f"YOLO={result.timing.yolo_ms:.0f}, "
            f"OCR={result.timing.ocr_ms:.0f}, "
            f"Matching={result.timing.matching_ms:.0f}, "
            f"Pipeline={result.timing.total_ms:.0f}"
        )

    print(f"Duvar saati (ms): {wall_ms:.0f}")

    boxes = []
    for box in result.medicines:
        label = box.medicine_name or box.status
        print(
            f"  Kutu {box.box_index}: {label} "
            f"(skor={box.matching_score:.1f})"
        )
        boxes.append(
            {
                "box_index": box.box_index,
                "status": box.status,
                "medicine_name": box.medicine_name,
                "matching_score": box.matching_score,
            }
        )

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "mode": args.mode,
            "image": str(args.image),
            "success": result.success,
            "detection_count": result.detection_count,
            "wall_ms": round(wall_ms, 1),
            "timing": timing_payload,
            "boxes": boxes,
        }
        args.json_out.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"JSON report: {args.json_out}")


if __name__ == "__main__":
    main()

