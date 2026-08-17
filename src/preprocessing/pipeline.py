from src.preprocessing.color_operations import (
    apply_clahe,
    convert_to_grayscale,
)  # Imports only the helper functions defined earlier.
from src.preprocessing.filter_operations import (
    apply_median_blur,
)
from src.preprocessing.geometric_operations import (
    crop_image,
    resize_image,
)
from src.preprocessing.morphological_operations import (
    apply_closing,
    apply_opening,
)
from src.preprocessing.threshold_operations import (
    apply_adaptive_threshold,
)


def preprocess_for_ocr(
    image,
    resize_width: int | None = None,
    crop_region: tuple[int, int, int, int] | None = None,
    median_kernel_size: int = 5,
    clahe_clip_limit: float = 2.0,
    clahe_tile_grid_size: tuple[int, int] = (8, 8),
    adaptive_block_size: int = 11,
    adaptive_constant: int = 2,
    morphology_kernel_size: tuple[int, int] = (3, 3),
):
    """
    Preprocess an image for OCR.

    Processing order:
        1. Optional resize
        2. Optional crop
        3. Grayscale
        4. Median Blur
        5. CLAHE
        6. Adaptive Threshold
        7. Opening
        8. Closing

    Args:
        image:
            Image read by OpenCV.

        resize_width:
            Width to resize the image to while preserving aspect ratio.
            If None, resizing is not applied.

        crop_region:
            Crop area: (x, y, width, height).
            If None, cropping is not applied.

        median_kernel_size:
            Median Blur kernel size.

        clahe_clip_limit:
            CLAHE contrast limit.

        clahe_tile_grid_size:
            CLAHE regional grid size.

        adaptive_block_size:
            Neighborhood size for Adaptive Threshold.

        adaptive_c:
            Constant subtracted from the local threshold value.

        opening_kernel_size:
            Kernel size used by Opening.

        closing_kernel_size:
            Kernel size used by Closing.

    Returns:
        Binary image prepared for OCR.

    Raises:
        ValueError:
            If the image is empty or invalid.
    """

    if image is None:       # First check: prevent the program from crashing.
        raise ValueError(
            "Pipeline için geçerli bir görüntü gereklidir."
        )

    processed_image = image.copy()

    # Downscale very large images while preserving aspect ratio.
    if resize_width is not None:
        processed_image = resize_image(
            processed_image,
            width=resize_width,
        )

    # Crop the image if a specific region was provided.
    if crop_region is not None:
        x, y, width, height = crop_region

        processed_image = crop_image(
            image=processed_image,
            x=x,
            y=y,
            width=width,
            height=height,
        )

    # Remove color information and create a single-channel image.
    grayscale_image = convert_to_grayscale(
        processed_image
    )

    # Reduce small noise.
    blurred_image = apply_median_blur(
        grayscale_image,
        kernel_size=median_kernel_size,
    )

    # Increase local contrast.
    clahe_image = apply_clahe(
        blurred_image,
        clip_limit=clahe_clip_limit,
        tile_grid_size=clahe_tile_grid_size,
    )

    # Convert the image to binary.
    threshold_image = apply_adaptive_threshold(
        grayscale_image=clahe_image,
        max_value=255,
        block_size=adaptive_block_size,
        constant=adaptive_constant,
    )

    # Reduce small white noise.
    opened_image = apply_opening(
        threshold_image,
        kernel_size=morphology_kernel_size,
        iterations=1,
    )

    # Close small black gaps.
    final_image = apply_closing(
        opened_image,
        kernel_size=morphology_kernel_size,
        iterations=1,
    )

    return final_image
