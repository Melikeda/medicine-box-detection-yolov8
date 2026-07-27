"""Run the main production pipeline from the project root."""

import argparse

from src.services import PipelineConfig, PipelineManager, analyze_medicine_box

DEFAULT_IMAGE = "data/samples/samples3.jpg"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a medicine box image against the CSV database.",
    )
    parser.add_argument(
        "image",
        nargs="?",
        default=DEFAULT_IMAGE,
        help=f"Path to the medicine box image (default: {DEFAULT_IMAGE})",
    )
    parser.add_argument(
        "--mode",
        choices=["fast", "accurate"],
        default="fast",
        help="OCR mode: fast (~6 variants) or accurate (~52 variants)",
    )
    parser.add_argument(
        "--preload",
        action="store_true",
        help="Load models explicitly before analysis (shows load progress)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = PipelineConfig(ocr_mode=args.mode)

    print("Ana pipeline: analyze_medicine_box()")
    print(f"Gorsel: {args.image}")
    print(f"OCR modu: {config.ocr_mode}")
    print("CSV: data/database/medicines.csv")

    if config.ocr_mode == "accurate":
        print(
            "Not: accurate mod CPU'da cok uzun surebilir (50+ OCR varyanti)."
        )
    else:
        print("Not: fast mod ~6 OCR varyanti kullanir.")

    print()

    if args.preload:
        manager = PipelineManager.get_instance(config)
        manager.load()
        result = manager.analyze(args.image)
    else:
        result = analyze_medicine_box(
            args.image,
            config=config,
        )

    print("\n" + "=" * 50)
    print("SONUC")
    print("=" * 50)
    print(f"Success: {result.success}")

    if result.yolo_confidence is not None:
        print(f"YOLO confidence: {result.yolo_confidence:.2f}")

    print(f"OCR aday sayisi: {len(result.ocr_candidates)}")
    print(f"Filtrelenmis aday: {len(result.filtered_candidates)}")

    if result.success and result.medicine:
        medicine = result.medicine
        print(f"Ilac: {medicine.get('medicine_name')}")
        print(f"Skor: {result.match_score:.2f}")
        print(f"OCR metni: {result.best_ocr_text}")
        print(f"Etken madde: {medicine.get('active_ingredient')}")
        print(f"Doz: {medicine.get('dosage')}")
        return

    print(f"Hata: {result.error}")
    if result.ranked_matches:
        top = result.ranked_matches[0]
        print(
            f"En yakin aday: {top[0].get('medicine_name')} "
            f"({top[1]:.2f})"
        )


if __name__ == "__main__":
    main()
