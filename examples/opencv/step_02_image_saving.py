from pathlib import Path

from src.preprocessing.basic_operations import (
    read_image,
    save_image,
)


def main() -> None:
    """
    Okunan bir görüntünün diske kaydedilmesini örnekler.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_path = Path(
        "results/preprocessing/medicine_sample_copy.jpg"
    )

    image = read_image(image_path)

    save_image(image, output_path)

    print("Görüntü başarıyla kaydedildi.")
    print(f"Çıktı yolu: {output_path}")


if __name__ == "__main__":
    main()