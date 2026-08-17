# Thresholding helpers for OCR preprocessing.
import cv2


def apply_binary_threshold(
    grayscale_image,
    threshold_value: int = 127,
    max_value: int = 255,
):
    """
    Apply global binary thresholding to a grayscale image.

    Pixels above the threshold become max_value, and the rest become 0.

    Args:
        grayscale_image: Single-channel grayscale image.
        threshold_value: Threshold value.
        max_value: Maximum value assigned to white pixels.

    Returns:
        Binary image produced by thresholding.

    Raises:
        ValueError: If the image is not grayscale or parameters are invalid.
    """
    used_threshold, threshold_image = cv2.threshold(
        grayscale_image,
        threshold_value,
        max_value,
        cv2.THRESH_BINARY,
    )

    return used_threshold, threshold_image


def apply_adaptive_threshold(
    grayscale_image,
    max_value: int = 255,
    block_size: int = 11,
    constant: int = 2,
):
    """
    Apply adaptive thresholding to a grayscale image.

    Local threshold values are calculated for different image regions.
    This method can work better than normal binary thresholding when lighting is uneven.

    Args:
        grayscale_image: Single-channel grayscale image.
        max_value: Maximum value assigned to white pixels.
        block_size: Neighborhood size used for the local threshold calculation.
            Must be odd and greater than 1.
        c: Constant subtracted from the local threshold value.

    Returns:
        Binary image produced by adaptive thresholding.

    Raises:
        ValueError: If the image or parameters are invalid.
    """

    if grayscale_image.ndim != 2:
        raise ValueError(
            "Adaptive threshold uygulanacak görüntü "
            "grayscale ve tek kanallı olmalıdır."
        )

    if block_size <= 1 or block_size % 2 == 0:
        raise ValueError(
            "block_size değeri 1'den büyük ve tek sayı olmalıdır."
        )

    adaptive_threshold_image = cv2.adaptiveThreshold(
        grayscale_image,
        max_value,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        constant,
    )

    return adaptive_threshold_image
