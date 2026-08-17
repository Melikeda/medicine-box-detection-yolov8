# Provides helpers to read, save, and display images.
from pathlib import Path

import cv2


def read_image(image_path: Path):
    """
    Read an image from the given file path with OpenCV.

    Args:
        image_path: Path to the image to read.

    Returns:
        Image read by OpenCV as a NumPy array.

    Raises:
        FileNotFoundError: If the image cannot be read.
    """

    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(
            f"Görüntü okunamadı. Dosya yolunu kontrol et: {image_path}"
        )

    return image


def save_image(image, output_path: Path) -> None:
    """
    Save the image to the specified file path.

    Args:
        image: OpenCV image to save.
        output_path: Output file path.

    Raises:
        RuntimeError: If the image cannot be saved.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    success = cv2.imwrite(
        str(output_path),
        image
    )

    if not success:
        raise RuntimeError(
            f"Görüntü kaydedilemedi: {output_path}"
        )


def display_image(
    image,
    window_name: str = "Image"
) -> None:
    """
    Display the image in an OpenCV window.

    Args:
        image: OpenCV image to display.
        window_name: Title of the window to open.
    """

    cv2.imshow(window_name, image)

    cv2.waitKey(0)

    cv2.destroyAllWindows()
