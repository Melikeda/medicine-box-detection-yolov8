"""
Crop regions of interest from an image.

Run:
    python -m examples.preprocessing.step_07_crop
"""

from pathlib import Path

import cv2

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.geometric_operations import (
    crop_image,
    resize_image,
)


def main() -> None:
    """
    Demonstrates cropping an image region.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_path = Path(
        "results/preprocessing/medicine_sample_crop.jpg"
    )

    # Read the image.
    image = read_image(image_path)

    print("\n===== CROP INFORMATION =====")
    print(f"Orijinal Shape : {image.shape}")

    # -------------------------------------------------
    # Area to crop
    # -------------------------------------------------
    x = 700
    y = 405
    width = 2350
    height = 1020

    # Apply the crop operation.
    cropped_image = crop_image(
        image=image,
        x=x,
        y=y,
        width=width,
        height=height,
    )

    print(f"Kırpılmış Shape : {cropped_image.shape}")

    # Save the crop result.
    save_image(
        cropped_image,
        output_path,
    )

    print(f"\nGörüntü kaydedildi: {output_path}")

    # -------------------------------------------------
    # Show the crop area on the original image.
    # -------------------------------------------------

    preview_image = image.copy()

    cv2.rectangle(
        preview_image,
        (x, y),
        (x + width, y + height),
        (0, 255, 0),
        thickness=10,
    )

    # Shrink the large image to fit on screen.
    preview_image = resize_image(
        preview_image,
        width=800,
    )

    # Shrink the crop result to fit on screen as well.
    cropped_preview = resize_image(
        cropped_image,
        width=800,
    )

    print("\nÖnce seçilen crop alanı gösterilecektir.")
    display_image(
        preview_image,
        window_name="Selected Crop Area",
    )

    print("Şimdi kırpılmış görüntü gösterilecektir.")
    display_image(
        cropped_preview,
        window_name="Cropped Image",
    )


if __name__ == "__main__":
    main()
