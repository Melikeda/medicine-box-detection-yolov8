from pathlib import Path

from src.ocr.ocr_pipeline import run_ocr_pipeline
from src.ocr.ocr_reader import create_ocr_reader


def print_ocr_results(
    results: list,
) -> None:
    """
    OCR sonuçlarını terminale düzenli şekilde yazdırır.
    """
    print("\nOCR PIPELINE SONUÇLARI")
    print("-" * 60)

    if not results:
        print("Herhangi bir metin bulunamadı.")
        return

    for index, result in enumerate(results, start=1):
        _, text, confidence = result

        print(
            f"{index}. {text} "
            f"| Güven: {confidence:.4f}"
        )


def main() -> None:
    input_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_path = Path(
        "results/ocr/pipeline/"
        "medicine_sample_preprocessed.jpg"
    )

    print("OCR okuyucusu hazırlanıyor...")

    reader = create_ocr_reader(
        languages=["tr", "en"],
        use_gpu=False,
    )

    print("OCR pipeline çalıştırılıyor...")

    results = run_ocr_pipeline(
        reader=reader,
        image_path=input_path,
        save_preprocessed_image=True,
        output_path=output_path,
    )

    print_ocr_results(results)

    print(
        f"\nİşlenmiş görüntü kaydedildi: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()