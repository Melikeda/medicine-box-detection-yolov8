"""
Apply global thresholding for binarization.

Run:
    python -m examples.preprocessing.step_09_threshold
"""

from pathlib import Path

import numpy as np

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
from src.preprocessing.threshold_operations import (
    apply_binary_threshold,
)


def main() -> None:
    """
    Demonstrates applying binary thresholding to a grayscale image.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    grayscale_output_path = Path(
        "results/preprocessing/medicine_sample_grayscale.jpg"
    )

    threshold_output_path = Path(
        "results/preprocessing/medicine_sample_threshold.jpg"
    )

    # Read the color image.
    image = read_image(image_path)

    # Thresholding expects a single-channel image, so
    # convert the image to grayscale first.
    grayscale_image = convert_to_grayscale(image)

    # Apply binary thresholding to the grayscale image.
    used_threshold, threshold_image = apply_binary_threshold(
        grayscale_image=grayscale_image,
        threshold_value=127,
        max_value=255,
    )

    print("\n===== THRESHOLD INFORMATION =====")

    print(f"Kullanılan threshold değeri : {used_threshold}")
    print(f"Grayscale shape             : {grayscale_image.shape}")
    print(f"Threshold shape             : {threshold_image.shape}")
    print(f"Grayscale ilk piksel        : {grayscale_image[0, 0]}")
    print(f"Threshold ilk piksel        : {threshold_image[0, 0]}")

    # Display the unique pixel values in the threshold image.
    unique_values = np.unique(threshold_image)

    print(f"Threshold piksel değerleri  : {unique_values}")

    # Save the grayscale and threshold results.
    save_image(
        grayscale_image,
        grayscale_output_path,
    )

    save_image(
        threshold_image,
        threshold_output_path,
    )

    print(
        f"\nGrayscale görüntü kaydedildi: "
        f"{grayscale_output_path}"
    )

    print(
        f"Threshold görüntü kaydedildi: "
        f"{threshold_output_path}"
    )

    # Shrink large images only for screen display.
    grayscale_preview = resize_image(
        grayscale_image,
        width=800,
    )

    threshold_preview = resize_image(
        threshold_image,
        width=800,
    )

    print("\nÖnce grayscale görüntü gösterilecektir.")

    display_image(
        grayscale_preview,
        window_name="Grayscale Image",
    )

    print("Şimdi threshold görüntü gösterilecektir.")

    display_image(
        threshold_preview,
        window_name="Binary Threshold Image",
    )


if __name__ == "__main__":
    main()
