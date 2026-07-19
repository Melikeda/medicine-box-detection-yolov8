from pathlib import Path

from src.integration.yolo_ocr_pipeline import (
    load_yolo_model,
    run_yolo_ocr_pipeline,
)
from src.ocr.ocr_reader import create_ocr_reader


def main() -> None:
    model_path = Path(
        "runs/detect/runs/detect/"
        "medicine_box_yolov8n-2/weights/best.pt"
    )

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_directory = Path(
        "results/ocr/yolo_ocr_integration"
    )

    print("YOLO modeli yükleniyor...")

    model = load_yolo_model(
        model_path=model_path,
    )

    print("OCR okuyucusu hazırlanıyor...")

    reader = create_ocr_reader(
        languages=["tr", "en"],
        use_gpu=False,
    )

    print("YOLO + OCR pipeline çalıştırılıyor...")

    results = run_yolo_ocr_pipeline(
        model=model,
        reader=reader,
        image_path=image_path,
        output_directory=output_directory,
        detection_confidence=0.25,
        ocr_confidence=0.70,
    )

    print("\nYOLO + OCR SONUÇLARI")
    print("-" * 60)

    if not results:
        print("Herhangi bir ilaç kutusu tespit edilemedi.")
        return

    for result in results:
        print(
            f"\nTespit No: "
            f"{result['detection_number']}"
        )

        print(
            f"Sınıf ID: "
            f"{result['class_id']}"
        )

        print(
            f"YOLO güven skoru: "
            f"{result['detection_confidence']:.4f}"
        )

        print(
            f"Bounding box: "
            f"{result['bounding_box']}"
        )

        print(
            f"Crop görüntüsü: "
            f"{result['crop_path']}"
        )

        print(
            f"İşlenmiş görüntü: "
            f"{result['preprocessed_path']}"
        )

        print("\nOkunan metinler:")

        texts = result["texts"]

        if not texts:
            print("- Metin bulunamadı.")
        else:
            for text in texts:
                print(f"- {text}")

        print(
            "\nBirleştirilmiş metin: "
            f"{result['combined_text']}"
        )

        print("-" * 60)


if __name__ == "__main__":
    main()