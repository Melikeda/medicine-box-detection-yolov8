"""
Convert color images to grayscale.

Run:
    python -m examples.preprocessing.step_08_grayscale
"""

from pathlib import Path

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.color_operations import (
    convert_to_grayscale,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)


def main() -> None:
    """
    Demonstrates converting a color image to grayscale.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_path = Path(
        "results/preprocessing/medicine_sample_grayscale.jpg"
    )

    # Read the color image.
    image = read_image(image_path)

    # Convert the image to grayscale.
    grayscale_image = convert_to_grayscale(image)

    print("\n===== GRAYSCALE INFORMATION =====")

    print(f"Renkli görüntü shape    : {image.shape}")
    print(f"Grayscale görüntü shape : {grayscale_image.shape}")

    print(f"Renkli görüntü ndim     : {image.ndim}")
    print(f"Grayscale görüntü ndim  : {grayscale_image.ndim}")

    print(f"Renkli ilk piksel       : {image[0, 0]}")
    print(f"Grayscale ilk piksel    : {grayscale_image[0, 0]}")

    # Save the grayscale image to disk.
    save_image(
        grayscale_image,
        output_path,
    )

    print(f"\nGrayscale görüntü kaydedildi: {output_path}")

    # Shrink the large color image for display only.
    color_preview = resize_image(
        image,
        width=800,
    )

    # Shrink the grayscale image for display only.
    grayscale_preview = resize_image(
        grayscale_image,
        width=800,
    )

    print("\nÖnce renkli görüntü gösterilecektir.")

    display_image(
        color_preview,
        window_name="Original Color Image",
    )

    print("Şimdi grayscale görüntü gösterilecektir.")

    display_image(
        grayscale_preview,
        window_name="Grayscale Image",
    )


if __name__ == "__main__":
    main()
