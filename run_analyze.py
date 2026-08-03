"""Run the main production pipeline from the project root."""

import argparse
import json

from src.services import (
    PipelineConfig,
    PipelineManager,
    analyze_medicine_boxes,
)

DEFAULT_IMAGE = "data/samples/samples3.jpg"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze medicine box images against the CSV database. "
            "Supports single and multi-box photos."
        ),
    )
    parser.add_argument(
        "--image",
        default=DEFAULT_IMAGE,
        help=f"Path to the image file (default: {DEFAULT_IMAGE})",
    )
    parser.add_argument(
        "--mode",
        choices=["fast", "accurate"],
        default="fast",
        help="OCR mode: fast (~4 variants/box, early exit) or accurate (~52 variants/box)",
    )
    parser.add_argument(
        "--preload",
        action="store_true",
        help="Load models explicitly before analysis (shows load progress)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print structured JSON output",
    )
    return parser.parse_args()


def print_box_results(result) -> None:
    print("\n" + "=" * 50)
    print("SONUC")
    print("=" * 50)
    print(f"Success: {result.success}")
    print(f"Gorsel: {result.image_path}")
    print(f"Tespit sayisi: {result.detection_count}")
    print(f"CSV ilac sayisi: {result.medicines_compared}")

    if result.error and result.detection_count == 0:
        print(f"Hata: {result.error}")
        return

    if result.timing:
        print(
            f"\nSure (ms): YOLO={result.timing.yolo_ms:.0f}, "
            f"OCR={result.timing.ocr_ms:.0f}, "
            f"Matching={result.timing.matching_ms:.0f}, "
            f"Toplam={result.timing.total_ms:.0f}"
        )

    for box in result.medicines:
        print(f"\n--- Kutu {box.box_index}/{result.detection_count} ---")
        print(f"YOLO confidence: {box.yolo_confidence:.2f}")
        print(f"BBox: {box.bounding_box.to_dict()}")
        print(f"Status: {box.status}")
        print(f"Mesaj: {box.display_message}")

        if box.ocr_text:
            print(f"OCR metni: {box.ocr_text}")

        if box.medicine_name:
            print(f"Ilac: {box.medicine_name}")
            print(f"Skor: {box.matching_score:.2f}")
        elif box.status == "not_medicine_box":
            if box.ocr_text:
                print(f"OCR metni: {box.ocr_text}")
            print(f"Not: {box.display_message}")
        elif box.best_candidate:
            print(
                f"En yakin aday: {box.best_candidate} "
                f"({box.matching_score:.2f})"
            )

        if box.error:
            print(f"Hata: {box.error}")


def main() -> None:
    args = parse_args()
    config = PipelineConfig(ocr_mode=args.mode)

    print("Ana pipeline: analyze_medicine_boxes()")
    print(f"Gorsel: {args.image}")
    print(f"OCR modu: {config.ocr_mode}")
    print("CSV: data/database/medicines.csv")

    if config.ocr_mode == "accurate":
        print(
            "Not: accurate mod CPU'da cok uzun surebilir "
            "(kutu basina 50+ OCR varyanti)."
        )
    else:
        print(
            "Not: fast mod kutu basina ~4 OCR varyanti kullanir "
            "(2 aci x 2; erken eslesmede daha az)."
        )

    print()

    if args.preload:
        manager = PipelineManager.get_instance(config)
        manager.load()
        result = manager.analyze_all(args.image)
    else:
        result = analyze_medicine_boxes(
            args.image,
            config=config,
        )

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print_box_results(result)


if __name__ == "__main__":
    main()
