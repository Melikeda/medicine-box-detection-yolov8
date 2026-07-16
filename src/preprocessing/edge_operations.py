import cv2


def apply_canny_edge_detection(
    image,
    threshold1: int = 100,
    threshold2: int = 200,
):
    """
    Görüntüye Canny Edge Detection uygular.

    Canny algoritması görüntüdeki
    keskin parlaklık değişimlerini
    tespit ederek kenarları çıkarır.

    Args:
        image:
            Grayscale görüntü.

        threshold1:
            Alt eşik değeri.

        threshold2:
            Üst eşik değeri.

    Returns:
        Kenar görüntüsü.
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