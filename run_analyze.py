"""Run the main production pipeline once from the project root."""

from src.services import PipelineConfig, analyze_medicine_box

IMAGE_PATH = "data/samples/samples3.jpg"


def main() -> None:
    print("Ana pipeline: analyze_medicine_box()")
    print(f"Gorsel: {IMAGE_PATH}")
    print("CSV: data/database/medicines.csv")
    print("CPU OCR uzun surebilir, lutfen bekleyin...\n")

    result = analyze_medicine_box(
        IMAGE_PATH,
        config=PipelineConfig(),
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
