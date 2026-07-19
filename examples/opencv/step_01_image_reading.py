from pathlib import Path

from src.preprocessing.basic_operations import read_image


def main() -> None:
    """
    OpenCV ile görüntü okuma işlemini örnekler.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    image = read_image(image_path)

    print("Görüntü başarıyla okundu.")
    print(f"Görüntü boyutu: {image.shape}")
    print(f"Python tipi: {type(image)}")
    print(f"Piksel veri tipi: {image.dtype}")
    print(f"Boyut sayısı: {image.ndim}")
    print(f"Toplam eleman sayısı: {image.size}")


if __name__ == "__main__":
    main()