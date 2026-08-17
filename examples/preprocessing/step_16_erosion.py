"""
Morphological erosion on binary images.

Run:
    python -m examples.preprocessing.step_16_erosion
"""

from pathlib import Path

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.color_operations import (
    apply_clahe,
    convert_to_grayscale,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)
from src.preprocessing.morphological_operations import (
    apply_erosion,
)
from src.preprocessing.threshold_operations import (
    apply_adaptive_threshold,
)


def main() -> None:
    """
    Compares how different kernel sizes affect Erosion results.

    Compared images:
        1. Adaptive Threshold image
        2. Erosion with a 3x3 kernel
        3. Erosion with a 7x7 kernel
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_directory = Path(
        "results/preprocessing/erosion_comparison"
    )

    # Read the color image.
    image = read_image(image_path)

    # Convert the image to grayscale.
    grayscale_image = convert_to_grayscale(
        image
    )

    # Increase local contrast.
    clahe_image = apply_clahe(
        grayscale_image,
        clip_limit=2.0,
        tile_grid_size=(8, 8),
    )

    # Morphological operations are easier to inspect
    # on binary images, so apply thresholding.
    threshold_image = apply_adaptive_threshold(
        grayscale_image=clahe_image,
        max_value=255,
        block_size=11,
        constant=2,
    )

    # Apply light Erosion with a small kernel.
    erosion_3x3 = apply_erosion(
        threshold_image,
        kernel_size=(3, 3),
        iterations=1,
    )

    # Apply stronger Erosion with a large kernel.
    erosion_7x7 = apply_erosion(
        threshold_image,
        kernel_size=(7, 7),
        iterations=1,
    )

    print("\n===== EROSION COMPARISON =====")

    print(f"Threshold Shape : {threshold_image.shape}")
    print(f"3x3 Shape       : {erosion_3x3.shape}")
    print(f"7x7 Shape       : {erosion_7x7.shape}")

    print("\n3x3 kernel → Daha hafif aşındırma")
    print("7x7 kernel → Daha güçlü aşındırma")

    # Save the results.
    save_image(
        threshold_image,
        output_directory / "01_threshold.jpg",
    )

    save_image(
        erosion_3x3,
        output_directory / "02_erosion_3x3.jpg",
    )

    save_image(
        erosion_7x7,
        output_directory / "03_erosion_7x7.jpg",
    )

    print(
        "\nKarşılaştırma görüntüleri kaydedildi: "
        f"{output_directory}"
    )

    # Shrink large images for display only.
    threshold_preview = resize_image(
        threshold_image,
        width=800,
    )

    erosion_3x3_preview = resize_image(
        erosion_3x3,
        width=800,
    )

    erosion_7x7_preview = resize_image(
        erosion_7x7,
        width=800,
    )

    print("\nÖnce Threshold görüntüsü gösterilecektir.")

    display_image(
        threshold_preview,
        window_name="Adaptive Threshold Image",
    )

    print("Şimdi 3x3 Erosion görüntüsü gösterilecektir.")

    display_image(
        erosion_3x3_preview,
        window_name="Erosion - 3x3 Kernel",
    )

    print("Şimdi 7x7 Erosion görüntüsü gösterilecektir.")

    display_image(
        erosion_7x7_preview,
        window_name="Erosion - 7x7 Kernel",
    )


if __name__ == "__main__":
    main()
