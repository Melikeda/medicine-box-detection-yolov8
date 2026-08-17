"""
Apply CLAHE for local contrast enhancement.

Run:
    python -m examples.preprocessing.step_15_clahe
"""

from pathlib import Path

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.color_operations import (
    apply_clahe,
    apply_histogram_equalization,
    convert_to_grayscale,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)


def main() -> None:
    """
    Compares Histogram Equalization and CLAHE results.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    histogram_output_path = Path(
        "results/preprocessing/"
        "medicine_sample_histogram_equalization.jpg"
    )

    clahe_output_path = Path(
        "results/preprocessing/"
        "medicine_sample_clahe.jpg"
    )

    # Read the color image.
    image = read_image(image_path)

    # Contrast operations expect a single-channel image, so
    # convert the image to grayscale.
    grayscale_image = convert_to_grayscale(
        image
    )

    # Apply global Histogram Equalization to the whole image.
    histogram_image = apply_histogram_equalization(
        grayscale_image
    )

    # Apply local CLAHE to small regions of the image.
    clahe_image = apply_clahe(
        grayscale_image,
        clip_limit=2.0,
        tile_grid_size=(8, 8),
    )

    print("\n===== CLAHE INFORMATION =====")

    print(f"Grayscale Shape : {grayscale_image.shape}")
    print(f"Histogram Shape : {histogram_image.shape}")
    print(f"CLAHE Shape     : {clahe_image.shape}")

    print(f"Grayscale ndim  : {grayscale_image.ndim}")
    print(f"Histogram ndim  : {histogram_image.ndim}")
    print(f"CLAHE ndim      : {clahe_image.ndim}")

    print(
        f"Grayscale piksel aralığı: "
        f"{grayscale_image.min()} - {grayscale_image.max()}"
    )

    print(
        f"Histogram piksel aralığı: "
        f"{histogram_image.min()} - {histogram_image.max()}"
    )

    print(
        f"CLAHE piksel aralığı    : "
        f"{clahe_image.min()} - {clahe_image.max()}"
    )

    # Save the results.
    save_image(
        histogram_image,
        histogram_output_path,
    )

    save_image(
        clahe_image,
        clahe_output_path,
    )

    print(
        f"\nHistogram görüntüsü kaydedildi: "
        f"{histogram_output_path}"
    )

    print(
        f"CLAHE görüntüsü kaydedildi: "
        f"{clahe_output_path}"
    )

    # Shrink large images for display only.
    grayscale_preview = resize_image(
        grayscale_image,
        width=800,
    )

    histogram_preview = resize_image(
        histogram_image,
        width=800,
    )

    clahe_preview = resize_image(
        clahe_image,
        width=800,
    )

    print("\nÖnce grayscale görüntü gösterilecektir.")

    display_image(
        grayscale_preview,
        window_name="Grayscale Image",
    )

    print(
        "Şimdi Histogram Equalization görüntüsü "
        "gösterilecektir."
    )

    display_image(
        histogram_preview,
        window_name="Histogram Equalization Image",
    )

    print("Şimdi CLAHE görüntüsü gösterilecektir.")

    display_image(
        clahe_preview,
        window_name="CLAHE Image",
    )


if __name__ == "__main__":
    main()
