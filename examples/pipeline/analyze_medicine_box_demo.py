"""
Recommended pipeline demo: analyze_medicine_box() public API.

This script demonstrates how to call the unified production pipeline
from src/services/. It does not reimplement pipeline logic.

Run:
    python -m examples.pipeline.analyze_medicine_box_demo
"""

from pathlib import Path

from src.services import PipelineConfig, analyze_medicine_box

DEFAULT_IMAGE = Path("data/samples/samples3.jpg")


def main() -> None:
    """Run the unified medicine box analysis pipeline."""
    config = PipelineConfig()
    image_path = DEFAULT_IMAGE

    if not image_path.exists():
        raise FileNotFoundError(
            f"Demo image not found: {image_path}"
        )

    print("Medicine Box Analysis — Pipeline Demo")
    print("=" * 50)
    print(f"Image: {image_path}")
    print(f"Model: {config.model_path}")
    print(f"Database: {config.medicines_csv_path}")
    print()
    print(
        "Not: CPU uzerinde OCR uzun surebilir (bulanik goruntulerde "
        "50+ varyant). pin_memory uyarisi hatadir, islem devam eder."
    )
    print("Lutfen bekleyin...\n")

    result = analyze_medicine_box(
        image_path=image_path,
        config=config,
        save_debug_outputs=False,
    )

    print(f"Success: {result.success}")

    if result.yolo_confidence is not None:
        print(f"YOLO confidence: {result.yolo_confidence:.2f}")

    print(f"OCR candidates: {len(result.ocr_candidates)}")
    print(
        "Filtered candidates: "
        f"{len(result.filtered_candidates)}"
    )
    print(
        "Medicines compared: "
        f"{result.medicines_compared}"
    )

    if result.success and result.medicine:
        medicine = result.medicine
        print()
        print("Best match")
        print("-" * 30)
        print(f"Name: {medicine.get('medicine_name', '-')}")
        print(f"Score: {result.match_score:.2f}")
        print(f"OCR text: {result.best_ocr_text}")
        print(
            "Active ingredient: "
            f"{medicine.get('active_ingredient', '-')}"
        )
        print(f"Dosage: {medicine.get('dosage', '-')}")
        print(f"Form: {medicine.get('form', '-')}")
        return

    print()
    print("No confident match found.")
    if result.error:
        print(f"Reason: {result.error}")

    if result.ranked_matches:
        best = result.ranked_matches[0]
        print(
            f"Top candidate: "
            f"{best[0].get('medicine_name', '-')} "
            f"({best[1]:.2f})"
        )


if __name__ == "__main__":
    main()
