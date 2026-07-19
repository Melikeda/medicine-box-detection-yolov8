from pathlib import Path
from typing import Any

import cv2
import easyocr
import numpy as np


def create_ocr_reader(
    languages: list[str] | None = None,
    use_gpu: bool = False,
) -> easyocr.Reader:
    """
    EasyOCR okuyucusunu oluşturur.

    Args:
        languages:
            OCR tarafından kullanılacak dil kodları.
            Varsayılan olarak Türkçe ve İngilizce kullanılır.
        use_gpu:
            True verilirse GPU kullanmayı dener.
            False verilirse CPU kullanır.

    Returns:
        Hazırlanmış EasyOCR Reader nesnesi.
    """
    if languages is None:
        languages = ["tr", "en"]

    reader = easyocr.Reader(
        languages,
        gpu=use_gpu,
    )

    return reader


def read_text_from_image(
    reader: easyocr.Reader,
    image_path: str | Path,
) -> list[Any]:
    """
    Verilen görüntüdeki yazıları OCR ile okur.

    Args:
        reader:
            Daha önce oluşturulmuş EasyOCR Reader nesnesi.
        image_path:
            Okunacak görüntünün dosya yolu.

    Returns:
        EasyOCR tarafından bulunan metin sonuçlarının listesi.

    Raises:
        FileNotFoundError:
            Görüntü dosyası bulunamazsa oluşur.
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Görüntü dosyası bulunamadı: {image_path}"
        )

    results = reader.readtext(str(image_path))

    return results


def draw_ocr_results(
    image_path: str | Path,
    results: list[Any],
    output_path: str | Path,
) -> None:
    """
    OCR sonuçlarını görüntü üzerine çizer ve kaydeder.

    Her metin için:
    - Metnin çevresine bir kutu çizer.
    - Okunan metni görüntüye yazar.
    - Güven skorunu metnin yanında gösterir.

    Args:
        image_path:
            Orijinal görüntünün dosya yolu.
        results:
            EasyOCR tarafından döndürülen OCR sonuçları.
        output_path:
            Sonuç görüntüsünün kaydedileceği dosya yolu.

    Raises:
        FileNotFoundError:
            Görüntü dosyası bulunamazsa veya okunamazsa oluşur.
        IOError:
            Sonuç görüntüsü kaydedilemezse oluşur.
    """
    image_path = Path(image_path)
    output_path = Path(output_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Görüntü dosyası bulunamadı: {image_path}"
        )

    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(
            f"Görüntü OpenCV ile okunamadı: {image_path}"
        )

    for result in results:
        bounding_box, text, confidence = result

        points = np.array(
            bounding_box,
            dtype=np.int32,
        )

        cv2.polylines(
            image,
            [points],
            isClosed=True,
            color=(0, 255, 0),
            thickness=3,
        )

        x = int(points[0][0])
        y = int(points[0][1])

        label = f"{text} ({confidence:.2f})"

        text_position = (
            x,
            max(y - 10, 30),
        )

        cv2.putText(
            image,
            label,
            text_position,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    success = cv2.imwrite(
        str(output_path),
        image,
    )

    if not success:
        raise IOError(
            f"Sonuç görüntüsü kaydedilemedi: {output_path}"
        )