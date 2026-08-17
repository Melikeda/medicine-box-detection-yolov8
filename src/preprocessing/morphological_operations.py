# These operations are used to improve letter shapes.
import cv2
import numpy as np


def create_kernel(
    kernel_size: tuple[int, int],
):
    """
    Create a rectangular kernel for morphological operations.

    Args:
        kernel_size:
            Kernel height and width.
            Values must be positive and odd.

    Returns:
        Kernel as a NumPy array.

    Raises:
        ValueError:
            If the kernel dimensions are invalid.
    """

    if (
        kernel_size[0] <= 0
        or kernel_size[1] <= 0
        or kernel_size[0] % 2 == 0
        or kernel_size[1] % 2 == 0
    ):
        raise ValueError(
            "Kernel boyutları pozitif ve tek sayı olmalıdır."
        )

    kernel = np.ones(
        kernel_size,
        dtype=np.uint8,
    )

    return kernel


def validate_iterations(
    iterations: int,
) -> None:
    """
    Validate the iteration count used by morphological operations.

    Args:
        iterations: Number of times the operation will be applied.

    Raises:
        ValueError: If iterations is not positive.
    """

    if iterations <= 0:
        raise ValueError(
            "iterations değeri pozitif olmalıdır."
        )


def apply_erosion(
    image,
    kernel_size: tuple[int, int] = (3, 3),
    iterations: int = 1,
):
    """
    Apply Erosion to the image.

    Erosion shrinks white regions and can reduce small white noise and thin protrusions.

    Args:
        image: Image to process with Erosion.
        kernel_size: Kernel size to use.
        iterations: Number of times to apply the operation.

    Returns:
        Image with Erosion applied.
    """

    validate_iterations(iterations)

    kernel = create_kernel(
        kernel_size
    )

    eroded_image = cv2.erode(
        image,
        kernel,
        iterations=iterations,
    )

    return eroded_image


def apply_dilation(
    image,
    kernel_size: tuple[int, int] = (3, 3),
    iterations: int = 1,
):
    """
    Apply Dilation to the image.

    Dilation enlarges white regions and can bring broken or thin white character parts closer together.

    Args:
        image: Image to process with Dilation.
        kernel_size: Kernel size to use.
        iterations: Number of times to apply the operation.

    Returns:
        Image with Dilation applied.
    """

    validate_iterations(iterations)

    kernel = create_kernel(
        kernel_size
    )

    dilated_image = cv2.dilate(
        image,
        kernel,
        iterations=iterations,
    )

    return dilated_image


def apply_opening(
    image,
    kernel_size: tuple[int, int] = (3, 3),
    iterations: int = 1,
):
    """
    Apply Opening to the image.

    Opening operation:

        Erosion
            then
        Dilation

    This can clean small white noise while preserving the shape of main white regions as much as possible.

    Args:
        image:
            Image to process with Opening.
        kernel_size:
            Kernel size to use.
        iterations:
            Number of times to apply the operation.

    Returns:
        Image with Opening applied.
    """

    validate_iterations(iterations)

    kernel = create_kernel(
        kernel_size
    )

    opened_image = cv2.morphologyEx(
        image,
        cv2.MORPH_OPEN,
        kernel,
        iterations=iterations,
    )

    return opened_image


def apply_closing(
    image,
    kernel_size: tuple[int, int] = (3, 3),
    iterations: int = 1,
):
    """
    Apply Closing to the image.

    Closing operation:

        Dilation
            then
        Erosion

    This can close small black gaps and merge nearby white regions.

    Args:
        image:
            Image to process with Closing.
        kernel_size:
            Kernel size to use.
        iterations:
            Number of times to apply the operation.

    Returns:
        Image with Closing applied.
    """

    validate_iterations(iterations)

    kernel = create_kernel(
        kernel_size
    )

    closed_image = cv2.morphologyEx(
        image,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=iterations,
    )

    return closed_image
