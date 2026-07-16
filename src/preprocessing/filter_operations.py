import cv2


def apply_gaussian_blur(
    image,
    kernel_size: tuple[int, int] = (5, 5),
    sigma: float = 0,
):
    """
    Görüntüye Gaussian Blur uygular.

    Gaussian Blur, görüntüdeki küçük gürültüleri azaltır
    ve görüntüyü yumuşatır.

    Args:
        image: Blur uygulanacak görüntü.
        kernel_size: Gaussian filtre boyutu.
            Her iki değer de pozitif ve tek sayı olmalıdır.
        sigma: Gaussian dağılımının standart sapması.
            0 verilirse OpenCV otomatik hesaplar.

    Returns:
        Gaussian Blur uygulanmış görüntü.

    Raises:
        ValueError: Kernel boyutları geçersizse.
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
    Görüntüye Median Blur uygular.

    Median Blur özellikle salt-and-pepper gürültüsünü
    azaltmada etkilidir.

    Args:
        image: Blur uygulanacak görüntü.
        kernel_size: Median filtre boyutu.
            1'den büyük ve tek sayı olmalıdır.

    Returns:
        Median Blur uygulanmış görüntü.

    Raises:
        ValueError: Kernel boyutu geçersizse.
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
    Görüntüye Bilateral Filter uygular.

    Bilateral Filter, görüntüdeki gürültüyü azaltırken
    yazı ve nesne kenarlarını mümkün olduğunca korur.

    Args:
        image: Filtre uygulanacak görüntü.
        diameter:
            Her piksel için incelenecek komşuluk alanının çapı.
            Değer büyüdükçe daha geniş bir çevre incelenir.
        sigma_color:
            Parlaklık veya renk farklarının filtre üzerindeki etkisi.
            Değer büyüdükçe farklı renkteki pikseller de
            yumuşatma işlemine daha fazla katılır.
        sigma_space:
            Pikseller arasındaki uzaklığın filtre üzerindeki etkisi.
            Değer büyüdükçe daha uzaktaki pikseller de dikkate alınır.

    Returns:
        Bilateral Filter uygulanmış görüntü.

    Raises:
        ValueError: Parametrelerden biri geçersizse.
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