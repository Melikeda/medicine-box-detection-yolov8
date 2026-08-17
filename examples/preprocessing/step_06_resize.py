"""
Resize images with OpenCV interpolation methods.

Run:
    python -m examples.preprocessing.step_06_resize
"""

from pathlib import Path

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)


def main() -> None:
    """
    Demonstrates resizing an image.
    """

    # Input image path.
    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    # Output image path.
    output_path = Path(
        "results/preprocessing/medicine_sample_resized.jpg"
    )

    # Read the image.
    image = read_image(image_path)

    # Resize the image to 800 pixels wide.
    resized_image = resize_image(
        image=image,
        width=800
    )

    print("\n===== RESIZE INFORMATION =====")

    print(f"Orijinal Shape : {image.shape}")
    print(f"Yeni Shape     : {resized_image.shape}")

    # Save the resized image.
    save_image(
        resized_image,
        output_path
    )

    print(f"\nGörüntü kaydedildi: {output_path}")

    # Display the resized image.
    display_image(
        resized_image,
        window_name="Resized Image"
    )


if __name__ == "__main__":
    main()
