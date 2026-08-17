# Clean noise from the image.
import cv2


def apply_gaussian_blur(
    image,
    kernel_size: tuple[int, int] = (5, 5),
    sigma: float = 0,
):
    """
    Apply Gaussian Blur to the image.

    Gaussian Blur reduces small noise in the image and smooths the image.

    Args:
        image: Image to blur.
        kernel_size: Gaussian filter size.
            Both values must be positive and odd.
        sigma: Standard deviation of the Gaussian distribution.
            If 0 is given, OpenCV calculates it automatically.

    Returns:
        Image with Gaussian Blur applied.

    Raises:
        ValueError: If the kernel dimensions are invalid.
    """

    if (
        kernel_size[0] <= 0
        or kernel_size[1] <= 0
        or kernel_size[0] % 2 == 0
        or kernel_size[1] % 2 == 0
    ):
        raise ValueError(
            "Gaussian kernel boyutları pozitif ve tek sayı olmalıdır."
        )

    blurred_image = cv2.GaussianBlur(
        image,
        kernel_size,
        sigma,
    )

    return blurred_image


def apply_median_blur(
    image,
    kernel_size: int = 5,
):
    """
    Apply Median Blur to the image.

    Median Blur is especially effective at reducing salt-and-pepper noise.

    Args:
        image: Image to blur.
        kernel_size: Median filter size.
            Must be odd and greater than 1.

    Returns:
        Image with Median Blur applied.

    Raises:
        ValueError: If the kernel size is invalid.
    """

    if kernel_size <= 1 or kernel_size % 2 == 0:
        raise ValueError(
            "Median kernel boyutu 1'den büyük ve tek sayı olmalıdır."
        )

    blurred_image = cv2.medianBlur(
        image,
        kernel_size,
    )

    return blurred_image


def apply_bilateral_filter(
    image,
    diameter: int = 9,
    sigma_color: float = 75,
    sigma_space: float = 75,
):
    """
    Apply a bilateral filter to the image.

    The filter reduces noise while preserving text and object edges.

    Args:
        image: Image to filter.
        diameter:
            Neighborhood diameter around each pixel.
            Larger values inspect a wider area.
        sigma_color:
            How strongly brightness/color differences affect the filter.
            Larger values let more dissimilar colors participate in smoothing.
        sigma_space:
            How strongly pixel distance affects the filter.
            Larger values include farther pixels.

    Returns:
        Bilaterally filtered image.

    Raises:
        ValueError: If a parameter is invalid.
    """

    if diameter <= 0:
        raise ValueError(
            "diameter değeri pozitif olmalıdır."
        )

    if sigma_color <= 0:
        raise ValueError(
            "sigma_color değeri pozitif olmalıdır."
        )

    if sigma_space <= 0:
        raise ValueError(
            "sigma_space değeri pozitif olmalıdır."
        )

    filtered_image = cv2.bilateralFilter(
        image,
        diameter,
        sigma_color,
        sigma_space,
    )

    return filtered_image
