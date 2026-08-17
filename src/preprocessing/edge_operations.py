# Added for modularity; it is not currently used by the OCR pipeline.
import cv2


def apply_canny_edge_detection(
    image,
    threshold1: int = 100,
    threshold2: int = 200,
):
    """
    Apply Canny Edge Detection to the image.

    The Canny algorithm extracts edges by detecting sharp brightness changes in the image.

    Args:
        grayscale_image: Grayscale image.
        threshold1: Lower threshold value.
        threshold2: Upper threshold value.

    Returns:
        Edge image.
    """

    if image.ndim != 2:
        raise ValueError(
            "Canny Edge Detection için grayscale görüntü gereklidir."
        )

    if threshold1 < 0 or threshold2 < 0:
        raise ValueError(
            "Threshold değerleri negatif olamaz."
        )

    edges = cv2.Canny(
        image,
        threshold1,
        threshold2,
    )

    return edges
