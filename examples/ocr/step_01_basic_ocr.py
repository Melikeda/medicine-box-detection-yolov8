from pathlib import Path

from src.ocr.ocr_reader import (
    create_ocr_reader,
    draw_ocr_results,
    read_text_from_image,
)


def main() -> None:
    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_path = Path(
        "results/ocr/medicine_sample_ocr.jpg"
    )

    print("OCR okuyucusu hazırlanıyor...")

    reader = create_ocr_reader(
        languages=["tr", "en"],
        use_gpu=False,
    )

    print("Görüntü okunuyor...")

    results = read_text_from_image(
        reader=reader,
        image_path=image_path,
    )

    print("\nOCR Sonuçları")
    print("-" * 50)

    if not results:
        print(
            "Görüntüde herhangi bir metin bulunamadı."
        )
        return

    for index, result in enumerate(
        results,
        start=1,
    ):
        bounding_box, text, confidence = result

        print(f"\nSonuç {index}")
        print(f"Metin: {text}")
        print(f"Güven skoru: {confidence:.4f}")
        print(f"Koordinatlar: {bounding_box}")

    draw_ocr_results(
        image_path=image_path,
        results=results,
        output_path=output_path,
    )

    print(
        f"\nSonuç görüntüsü kaydedildi: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()