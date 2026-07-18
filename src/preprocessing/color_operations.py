#Bu yüzden resmi griye çeviriyoruz.
import cv2


def convert_to_grayscale(image):
    """
    BGR formatındaki renkli görüntüyü grayscale görüntüye dönüştürür.
    """

    grayscale_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    return grayscale_image


def apply_histogram_equalization(grayscale_image):
    """
    Grayscale görüntünün global kontrastını artırır.
    """

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
    Grayscale görüntüye CLAHE uygular.

    CLAHE, görüntüyü küçük bölgelere ayırarak
    yerel kontrastı artırır ve kontrast artışını sınırlar.

    Args:
        grayscale_image:
            CLAHE uygulanacak tek kanallı grayscale görüntü.
        clip_limit:
            Kontrast artışını sınırlayan değer.
            Değer büyüdükçe kontrast daha güçlü artabilir.
        tile_grid_size:
            Görüntünün bölüneceği yerel alanların düzeni.
            Örneğin (8, 8), görüntünün küçük bölgelere
            ayrılarak işleneceği anlamına gelir.

    Returns:
        CLAHE uygulanmış grayscale görüntü.

    Raises:
        ValueError:
            Görüntü grayscale değilse veya parametreler geçersizse.
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