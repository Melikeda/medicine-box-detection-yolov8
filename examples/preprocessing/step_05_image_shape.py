"""
Inspect image shape, dtype, and dimensions.

Run:
    python -m examples.preprocessing.step_05_image_shape
"""

from pathlib import Path

from src.preprocessing.basic_operations import read_image


def main() -> None:
    """
    Inspects an image's height, width, and channel information.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    image = read_image(image_path)

    # Shape information for the color image:
    # (height, width, channel count)
    height, width, channels = image.shape

    # Ratio of image width to height.
    aspect_ratio = width / height

    # Image center coordinates.
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
