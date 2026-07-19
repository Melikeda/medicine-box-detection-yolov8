from pathlib import Path

from src.preprocessing.basic_operations import read_image


def main() -> None:
    """
    Bir görüntünün yükseklik, genişlik ve kanal bilgilerini inceler.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    image = read_image(image_path)

    # Renkli görüntünün shape bilgisi:
    # (yükseklik, genişlik, kanal sayısı)
    height, width, channels = image.shape

    # Görüntünün genişliğinin yüksekliğine oranı.
    aspect_ratio = width / height

    # Görüntünün merkez koordinatları.
    center_x = width // 2
    center_y = height // 2

    print("===== IMAGE SHAPE INFORMATION =====")

    print(f"Shape: {image.shape}")
    print(f"Yükseklik: {height} piksel")
    print(f"Genişlik: {width} piksel")
    print(f"Kanal sayısı: {channels}")

    print(f"En-boy oranı: {aspect_ratio:.2f}")

    print(
        f"Görüntünün merkez koordinatı: "
        f"(x={center_x}, y={center_y})"
    )


if __name__ == "__main__":
    main()