# Convert images to grayscale because color information is not needed here.
import cv2


def convert_to_grayscale(image):
    """Convert a BGR color image to a grayscale image."""

    grayscale_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    return grayscale_image


def apply_histogram_equalization(grayscale_image):
    """Increase the global contrast of a grayscale image."""

    if grayscale_image.ndim != 2:
        raise ValueError(
            "Histogram Equalization için grayscale "
            "ve tek kanallı görüntü gereklidir."
        )

    equalized_image = cv2.equalizeHist(
        grayscale_image
    )

    return equalized_image


def apply_clahe(
    grayscale_image,
    clip_limit: float = 2.0,
    tile_grid_size: tuple[int, int] = (8, 8),
):
    """
    Apply CLAHE to a grayscale image.

    CLAHE divides the image into small regions, increases local contrast,
    and limits the contrast increase.

    Args:
        grayscale_image:
            Single-channel grayscale image to process with CLAHE.
        clip_limit:
            Value that limits contrast amplification.
            Larger values can increase contrast more strongly.
        tile_grid_size:
            Layout of the local regions into which the image is divided.
            For example, (8, 8) means the image is processed in small regions.

    Returns:
        Grayscale image processed with CLAHE.

    Raises:
        ValueError:
            If the image is not grayscale or parameters are invalid.
    """

    if grayscale_image.ndim != 2:
        raise ValueError(
            "CLAHE için grayscale ve tek kanallı görüntü gereklidir."
        )

    if clip_limit <= 0:
        raise ValueError(
            "clip_limit değeri pozitif olmalıdır."
        )

    if (
        tile_grid_size[0] <= 0
        or tile_grid_size[1] <= 0
    ):
        raise ValueError(
            "tile_grid_size değerleri pozitif olmalıdır."
        )

    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=tile_grid_size,
    )

    clahe_image = clahe.apply(
        grayscale_image
    )

    return clahe_image
