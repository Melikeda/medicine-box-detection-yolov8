import cv2
import numpy as np


def create_kernel(
    kernel_size: tuple[int, int],
):
    """
    Morfolojik işlemlerde kullanılacak dikdörtgen kernel oluşturur.

    Args:
        kernel_size:
            Kernel yüksekliği ve genişliği.
            Değerler pozitif ve tek sayı olmalıdır.

    Returns:
        NumPy dizisi biçimindeki kernel.

    Raises:
        ValueError:
            Kernel boyutları geçersizse.
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
    Morfolojik işlemlerde kullanılan tekrar sayısını doğrular.

    Args:
        iterations:
            İşlemin kaç kez uygulanacağı.

    Raises:
        ValueError:
            iterations pozitif değilse.
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
    Görüntüye Erosion uygular.

    Erosion, beyaz bölgeleri küçültür.
    Küçük beyaz gürültüleri ve ince çıkıntıları
    azaltmak için kullanılabilir.

    Args:
        image:
            Erosion uygulanacak görüntü.
        kernel_size:
            Kullanılacak kernel boyutu.
        iterations:
            İşlemin kaç kez uygulanacağı.

    Returns:
        Erosion uygulanmış görüntü.
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
    Görüntüye Dilation uygular.

    Dilation, beyaz bölgeleri büyütür.
    Kopmuş veya ince beyaz karakter parçalarını
    birbirine yaklaştırmak için kullanılabilir.

    Args:
        image:
            Dilation uygulanacak görüntü.
        kernel_size:
            Kullanılacak kernel boyutu.
        iterations:
            İşlemin kaç kez uygulanacağı.

    Returns:
        Dilation uygulanmış görüntü.
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
    Görüntüye Opening uygular.

    Opening işlemi:

        Erosion
            ↓
        Dilation

    sırasıyla uygulanır.

    Küçük beyaz gürültüleri temizlemek ve ana
    beyaz bölgelerin şeklini mümkün olduğunca
    korumak için kullanılabilir.

    Args:
        image:
            Opening uygulanacak görüntü.
        kernel_size:
            Kullanılacak kernel boyutu.
        iterations:
            İşlemin kaç kez uygulanacağı.

    Returns:
        Opening uygulanmış görüntü.
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
    Görüntüye Closing uygular.

    Closing işlemi:

        Dilation
            ↓
        Erosion

    sırasıyla uygulanır.

    Küçük siyah boşlukları kapatmak ve birbirine
    yakın beyaz bölgeleri birleştirmek için
    kullanılabilir.

    Args:
        image:
            Closing uygulanacak görüntü.
        kernel_size:
            Kullanılacak kernel boyutu.
        iterations:
            İşlemin kaç kez uygulanacağı.

    Returns:
        Closing uygulanmış görüntü.
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