from pathlib import Path

import cv2
import matplotlib.pyplot as plt

from src.preprocessing.basic_operations import read_image


def display_comparison(
    bgr_image,
    rgb_image
) -> None:
    """
    BGR ve RGB görüntülerini Matplotlib ile karşılaştırır.

    Matplotlib RGB kanal sırası beklediği için BGR görüntü
    doğrudan verildiğinde kırmızı ve mavi renkler yanlış görünür.
    """

    plt.figure(figsize=(10, 6))
    plt.imshow(bgr_image)
    plt.title("Yanlış Gösterim - BGR")
    plt.axis("off")

    plt.figure(figsize=(10, 6))
    plt.imshow(rgb_image)
    plt.title("Doğru Gösterim - RGB")
    plt.axis("off")

    plt.show()


def main() -> None:
    """
    OpenCV'nin BGR ve Matplotlib'in RGB kanal sırasını karşılaştırır.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    bgr_image = read_image(image_path)

    rgb_image = cv2.cvtColor(
        bgr_image,
        cv2.COLOR_BGR2RGB
    )

    print("===== PIXEL INFORMATION =====")
    print(f"İlk piksel (BGR): {bgr_image[0, 0]}")
    print(f"İlk piksel (RGB): {rgb_image[0, 0]}")

    display_comparison(
        bgr_image,
        rgb_image
    )


if __name__ == "__main__":
    main()