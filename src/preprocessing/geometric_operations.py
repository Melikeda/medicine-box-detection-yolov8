# Image geometry helpers.
import cv2


def resize_image(
    image,
    width: int | None = None,
    height: int | None = None,
):
    """Resize the image while preserving aspect ratio."""

    if width is None and height is None:
        raise ValueError(
            "Width veya height değerlerinden biri verilmelidir."
        )

    original_height, original_width = image.shape[:2]

    if width is not None:
        scale_ratio = width / original_width
        new_width = width
        new_height = int(original_height * scale_ratio)
    else:
        scale_ratio = height / original_height
        new_width = int(original_width * scale_ratio)
        new_height = height

    resized_image = cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA,
    )

    return resized_image


def crop_image(
    image,
    x: int,
    y: int,
    width: int,
    height: int,
):
    """
    Crop a specific region of the image.

    Args:
        image: Image to crop.
        x: Starting x coordinate.
        y: Starting y coordinate.
        width: Width of the cropped region.
        height: Height of the cropped region.

    Returns:
        Cropped image.
    """

    cropped_image = image[
        y:y + height,
        x:x + width
    ]

    return cropped_image
