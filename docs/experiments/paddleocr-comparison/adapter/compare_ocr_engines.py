"""
ARCHIVED snapshot — not part of the product CLI.

Used during the EasyOCR vs PaddleOCR trial. Current src/ has no ocr_engine
switch, so this script is not runnable against production code.
See docs/experiments/paddleocr-comparison/ and Report 26.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ocr.engine import paddleocr_is_available
from src.services.config import OCREngineName, PipelineConfig
from src.services.pipeline_manager import PipelineManager

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def _collect_images(image: Path | None, images_dir: Path | None) -> list[Path]:
    paths: list[Path] = []
    if image is not None:
        paths.append(image)
    if images_dir is not None:
        paths.extend(
            sorted(
                p
                for p in images_dir.iterdir()
                if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
            )
        )
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def _summarize_result(result: Any) -> dict[str, Any]:
    boxes = []
    for box in result.medicines:
        boxes.append(
            {
                "box_index": box.box_index,
                "status": box.status,
                "ocr_text": box.ocr_text,
                "medicine_name": box.medicine_name,
                "matching_score": round(float(box.matching_score), 2),
            }
        )
    timing = None
    if result.timing:
        timing = {
            "yolo_ms": round(result.timing.yolo_ms, 1),
            "ocr_ms": round(result.timing.ocr_ms, 1),
            "matching_ms": round(result.timing.matching_ms, 1),
            "total_ms": round(result.timing.total_ms, 1),
        }
    return {
        "success": result.success,
        "detection_count": result.detection_count,
        "error": result.error,
        "timing": timing,
        "boxes": boxes,
    }


def _run_engine(
    *,
    image: Path,
    mode: str,
    engine: OCREngineName,
) -> dict[str, Any]:
    PipelineManager.reset_instance()
    config = PipelineConfig(ocr_mode=mode, ocr_engine=engine)
    manager = PipelineManager.get_instance(config)
    started = time.perf_counter()
    manager.load()
    result = manager.analyze_all(image)
    wall_ms = (time.perf_counter() - started) * 1000
    manager.unload()
    PipelineManager.reset_instance()
    payload = _summarize_result(result)
    payload["engine"] = engine
    payload["wall_ms"] = round(wall_ms, 1)
    return payload


def _print_row(image: Path, easy: dict[str, Any], paddle: dict[str, Any]) -> None:
    def _label(payload: dict[str, Any]) -> str:
        if not payload["boxes"]:
            return payload.get("error") or "no_box"
        box = payload["boxes"][0]
        name = box.get("medicine_name") or box.get("status")
        text = box.get("ocr_text") or ""
        score = box.get("matching_score")
        return f"{name} | ocr={text!r} | {score} | {payload['wall_ms']:.0f}ms"

    print(f"\n{image}")
    print(f"  easyocr  : {_label(easy)}")
    print(f"  paddleocr: {_label(paddle)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare EasyOCR vs PaddleOCR on sample medicine-box photos.",
    )
    parser.add_argument("--image", type=Path, default=None)
    parser.add_argument("--images-dir", type=Path, default=None)
    parser.add_argument("--mode", choices=("fast", "accurate"), default="fast")
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    if args.image is None and args.images_dir is None:
        args.image = PROJECT_ROOT / "data" / "samples" / "parol_plus.jpg"

    images = _collect_images(args.image, args.images_dir)
    if not images:
        raise SystemExit("No images found.")
    missing = [str(path) for path in images if not path.exists()]
    if missing:
        raise SystemExit("Missing image(s): " + ", ".join(missing))

    if not paddleocr_is_available():
        raise SystemExit(
            "PaddleOCR is not installed.\n"
            "  pip install -r requirements-paddleocr.txt\n"
            "  .\\scripts\\setup-paddleocr.ps1\n"
            "EasyOCR default is unchanged."
        )

    print(f"Images: {len(images)}")
    print(f"Mode: {args.mode}")
    print("Running EasyOCR then PaddleOCR (YOLO reloads between engines).")

    rows: list[dict[str, Any]] = []
    for image in images:
        print(f"\n==> {image} [easyocr]")
        easy = _run_engine(image=image, mode=args.mode, engine="easyocr")
        print(f"==> {image} [paddleocr]")
        paddle = _run_engine(image=image, mode=args.mode, engine="paddleocr")
        _print_row(image, easy, paddle)
        rows.append(
            {
                "image": str(image),
                "mode": args.mode,
                "easyocr": easy,
                "paddleocr": paddle,
            }
        )

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(
                {"mode": args.mode, "results": rows},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"\nJSON: {args.json_out}")


if __name__ == "__main__":
    main()
