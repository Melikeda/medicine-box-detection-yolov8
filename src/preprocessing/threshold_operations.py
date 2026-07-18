#Tonlarla çeviri yapılıyor.
import cv2


def apply_binary_threshold(
    grayscale_image,
    threshold_value: int = 127,
    max_value: int = 255,
):
    """
    Grayscale görüntüye binary threshold uygular.

    Args:
        grayscale_image: Tek kanallı grayscale görüntü.
        threshold_value: Siyah ve beyaz ayrımında kullanılacak eşik değeri.
        max_value: Eşik üzerindeki piksellere atanacak maksimum değer.

    Returns:
        Kullanılan eşik değeri ve binary threshold görüntüsü.

    Raises:
        ValueError: Görüntü grayscale değilse.
    """

    if grayscale_image.ndim != 2:
        raise ValueError(
            "Threshold uygulanacak görüntü grayscale ve tek kanallı olmalıdır."
        )

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
    Grayscale görüntüye adaptive threshold uygular.

    Görüntünün farklı bölgeleri için yerel eşik değerleri hesaplanır.
    Bu yöntem, ışığın görüntünün her yerinde eşit olmadığı durumlarda
    normal binary threshold yönteminden daha başarılı olabilir.

    Args:
        grayscale_image: Tek kanallı grayscale görüntü.
        max_value: Beyaz piksellere atanacak maksimum değer.
        block_size: Yerel eşik hesabında kullanılacak komşuluk boyutu.
            Tek sayı ve 1'den büyük olmalıdır.
        constant: Hesaplanan yerel eşik değerinden çıkarılacak sabit.

    Returns:
        Adaptive threshold uygulanmış siyah-beyaz görüntü.

    Raises:
        ValueError: Görüntü grayscale değilse veya block_size geçersizse.
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