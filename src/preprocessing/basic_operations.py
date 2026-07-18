#Bunlar resmi okumayı, kaydetmeyi ve göstermeyi sağlar.
from pathlib import Path

import cv2


def read_image(image_path: Path):
    """
    Verilen dosya yolundaki görüntüyü OpenCV ile okur.

    Args:
        image_path: Okunacak görüntünün dosya yolu.

    Returns:
        OpenCV tarafından NumPy dizisi olarak okunan görüntü.

    Raises:
        FileNotFoundError: Görüntü okunamazsa.
    """

    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(
            f"Görüntü okunamadı. Dosya yolunu kontrol et: {image_path}"
        )

    return image


def save_image(image, output_path: Path) -> None:
    """
    Görüntüyü belirtilen dosya yoluna kaydeder.

    Args:
        image: Kaydedilecek OpenCV görüntüsü.
        output_path: Çıktı dosyasının yolu.

    Raises:
        RuntimeError: Görüntü kaydedilemezse.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    success = cv2.imwrite(
        str(output_path),
        image
    )

    if not success:
        raise RuntimeError(
            f"Görüntü kaydedilemedi: {output_path}"
        )


def display_image(
    image,
    window_name: str = "Image"
) -> None:
    """
    Görüntüyü OpenCV penceresinde gösterir.

    Args:
        image: Gösterilecek OpenCV görüntüsü.
        window_name: Açılacak pencerenin başlığı.
    """

    cv2.imshow(window_name, image)

    cv2.waitKey(0)

    cv2.destroyAllWindows()