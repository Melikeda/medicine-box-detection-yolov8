
from pathlib import Path

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.color_operations import (
    convert_to_grayscale,
    apply_clahe,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)
from src.preprocessing.morphological_operations import (
    apply_closing,
)
from src.preprocessing.threshold_operations import (
    apply_adaptive_threshold,
)


def main():
    """
    Closing işlemini örnekler.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_path = Path(
        "results/preprocessing/medicine_sample_closing.jpg"
    )

    image = read_image(
        image_path
    )

    grayscale = convert_to_grayscale(
        image
    )

    clahe = apply_clahe(
        grayscale
    )

    threshold = apply_adaptive_threshold(
        grayscale_image=clahe,
        max_value=255,
        block_size=11,
        constant=2,
    )

    closing = apply_closing(
        threshold,
        kernel_size=(3, 3),
        iterations=1,
    )

    print("\n===== CLOSING INFORMATION =====")

    print(f"Threshold Shape : {threshold.shape}")
    print(f"Closing Shape   : {closing.shape}")

    save_image(
        closing,
        output_path,
    )

    threshold_preview = resize_image(
        threshold,
        width=800,
    )

    closing_preview = resize_image(
        closing,
        width=800,
    )

    print("\nÖnce Threshold görüntüsü gösterilecektir.")

    display_image(
        threshold_preview,
        "Threshold Image",
    )

    print("Şimdi Closing görüntüsü gösterilecektir.")

    display_image(
        closing_preview,
        "Closing Image",
    )


if __name__ == "__main__":
    main()