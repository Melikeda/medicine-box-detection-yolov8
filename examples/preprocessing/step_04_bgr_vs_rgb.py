"""
Understand BGR vs RGB color channel order in OpenCV.

Run:
    python -m examples.preprocessing.step_04_bgr_vs_rgb
"""

from pathlib import Path

import cv2
import matplotlib.pyplot as plt

from src.preprocessing.basic_operations import read_image


def display_comparison(
    bgr_image,
    rgb_image
) -> None:
    """
    Compare BGR and RGB images with Matplotlib.

    Matplotlib expects RGB channel order, so red and blue colors
    look incorrect when a BGR image is passed directly.
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
    Compare OpenCV's BGR channel order with Matplotlib's RGB order.
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