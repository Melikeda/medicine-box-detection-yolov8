#Eğik açıları düzenliyor.
import cv2
import numpy as np


def order_points(points):
    """
    Dört köşe noktasını standart sıraya dizer.

    Sıralama:
        1. Sol üst
        2. Sağ üst
        3. Sağ alt
        4. Sol alt

    Args:
        points:
            Dört adet (x, y) koordinatı.

    Returns:
        Standart sıraya dizilmiş float32 NumPy dizisi.

    Raises:
        ValueError:
            Tam olarak dört nokta verilmemişse.
    """

    points = np.asarray(
        points,
        dtype=np.float32,
    )

    if points.shape != (4, 2):
        raise ValueError(
            "Perspective Transform için tam olarak "
            "dört adet (x, y) noktası verilmelidir."
        )

    ordered_points = np.zeros(
        (4, 2),
        dtype=np.float32,
    )

    # x + y toplamı en küçük olan nokta sol üst,
    # en büyük olan nokta sağ alt kabul edilir.
    coordinate_sum = points.sum(axis=1)

    ordered_points[0] = points[
        np.argmin(coordinate_sum)
    ]

    ordered_points[2] = points[
        np.argmax(coordinate_sum)
    ]

    # y - x farkı en küçük olan nokta sağ üst,
    # en büyük olan nokta sol alt kabul edilir.
    coordinate_difference = np.diff(
        points,
        axis=1,
    ).reshape(-1)

    ordered_points[1] = points[
        np.argmin(coordinate_difference)
    ]

    ordered_points[3] = points[
        np.argmax(coordinate_difference)
    ]

    return ordered_points


def apply_perspective_transform(
    image,
    source_points,
):
    """
    Dört köşe noktasını kullanarak görüntüyü düzleştirir.

    Args:
        image:
            Perspective Transform uygulanacak görüntü.

        source_points:
            Görüntüdeki dört köşe koordinatı.
            Noktaların sırası fark etmez; fonksiyon
            bunları standart sıraya dizer.

    Returns:
        Perspective Transform uygulanmış görüntü.

    Raises:
        ValueError:
            Noktalar geçersizse veya çıktı boyutu hesaplanamazsa.
    """

    ordered_points = order_points(
        source_points
    )

    top_left = ordered_points[0]
    top_right = ordered_points[1]
    bottom_right = ordered_points[2]
    bottom_left = ordered_points[3]

    # Alt ve üst kenar uzunluklarını hesapla.
    bottom_width = np.linalg.norm(
        bottom_right - bottom_left
    )

    top_width = np.linalg.norm(
        top_right - top_left
    )

    max_width = int(
        max(bottom_width, top_width)
    )

    # Sol ve sağ kenar uzunluklarını hesapla.
    right_height = np.linalg.norm(
        top_right - bottom_right
    )

    left_height = np.linalg.norm(
        top_left - bottom_left
    )

    max_height = int(
        max(right_height, left_height)
    )

    if max_width <= 0 or max_height <= 0:
        raise ValueError(
            "Perspective Transform için hesaplanan "
            "çıktı boyutu geçersizdir."
        )

    destination_points = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
        ],
        dtype=np.float32,
    )

    transformation_matrix = cv2.getPerspectiveTransform(
        ordered_points,
        destination_points,
    )

    transformed_image = cv2.warpPerspective(
        image,
        transformation_matrix,
        (max_width, max_height),
    )

    return transformed_image