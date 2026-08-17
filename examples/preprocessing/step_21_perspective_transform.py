"""
Correct perspective distortion on box images.

Run:
    python -m examples.preprocessing.step_21_perspective_transform
"""

from pathlib import Path

import cv2
import numpy as np

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)
from src.preprocessing.perspective_operations import (
    apply_perspective_transform,
    order_points,
)


def draw_selected_points(
    image,
    points,
):
    """
    Marks the four corners selected for Perspective Transform
    on the image.

    Args:
        image:
            Image to mark.

        points:
            Four (x, y) coordinates.

    Returns:
        Image with marked points and boundary lines.
    """

    preview_image = image.copy()

    ordered_points = order_points(
        points
    ).astype(int)

    labels = [
        "Top Left",
        "Top Right",
        "Bottom Right",
        "Bottom Left",
    ]

    # Draw the four corners and labels.
    for index, point in enumerate(
        ordered_points
    ):
        x, y = point

        cv2.circle(
            preview_image,
            (x, y),
            radius=18,
            color=(0, 0, 255),
            thickness=-1,
        )

        cv2.putText(
            preview_image,
            labels[index],
            (x + 20, y - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 0, 255),
            thickness=3,
        )

    # Connect the selected four points with lines.
    cv2.polylines(
        preview_image,
        [
            ordered_points.reshape(
                (-1, 1, 2)
            )
        ],
        isClosed=True,
        color=(0, 255, 0),
        thickness=10,
    )

    return preview_image


def main() -> None:
    """
    Applies Perspective Transform using the four corners
    of a medicine box.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_path = Path(
        "results/preprocessing/"
        "medicine_sample_perspective_transform.jpg"
    )

    # Read the original image.
    image = read_image(
        image_path
    )

    print("\n===== PERSPECTIVE TRANSFORM INFORMATION =====")
    print(f"Orijinal Shape: {image.shape}")

    # Approximate four corner coordinates of the medicine box.
    #
    # Ordering is not required because order_points()
    # arranges them automatically.
    #
    # These values are approximate starting points
    # for the sample photo you use.
    source_points = np.array(
        [
            # Top left
            # Top right
            # Bottom right
            # Bottom left
        ],
        dtype=np.float32,
    )

    # Apply Perspective Transform.
    transformed_image = apply_perspective_transform(
        image=image,
        source_points=source_points,
    )

    print(
        f"Dönüştürülmüş Shape: "
        f"{transformed_image.shape}"
    )

    # Save the result.
    save_image(
        transformed_image,
        output_path,
    )

    print(
        f"Perspective Transform görüntüsü kaydedildi: "
        f"{output_path}"
    )

    # Show the selected points on the original image.
    selected_points_image = draw_selected_points(
        image,
        source_points,
    )

    # Shrink the images for screen display only.
    points_preview = resize_image(
        selected_points_image,
        width=800,
    )

    transformed_preview = resize_image(
        transformed_image,
        width=800,
    )

    print(
        "\nÖnce seçilen dört köşe noktası "
        "gösterilecektir."
    )

    display_image(
        points_preview,
        window_name="Selected Perspective Points",
    )

    print(
        "Şimdi Perspective Transform sonucu "
        "gösterilecektir."
    )

    display_image(
        transformed_preview,
        window_name="Perspective Transform Result",
    )


if __name__ == "__main__":
    main()
