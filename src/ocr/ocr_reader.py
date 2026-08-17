from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import cv2
import easyocr
import numpy as np


@runtime_checkable
class OCRReader(Protocol):
    """Minimal reader used by ``run_ocr_on_variant`` (EasyOCR ``readtext``)."""

    def readtext(
        self,
        image: Any,
        detail: int = 1,
        paragraph: bool = False,
    ) -> list[Any]:
        """Return EasyOCR-style ``[(bbox, text, confidence), ...]``."""


def create_ocr_reader(
    languages: list[str] | None = None,
    use_gpu: bool = False,
) -> easyocr.Reader:
    """
    Create an EasyOCR reader, defaulting to Turkish and English.

    Args:
        languages:
            Language codes used by OCR.
            Turkish and English are used by default.

        use_gpu:
            If True, try to use the GPU.
            If False, use the CPU.
    """
    if languages is None:
        languages = ["tr", "en"]

    return easyocr.Reader(
        languages,
        gpu=use_gpu,
    )


def read_text_from_image(
    reader: OCRReader,
    image_path: str | Path,
) -> list[Any]:
    """
    Read text from the given image with OCR.

    Args:
        reader:
            A previously created EasyOCR Reader instance.

        image_path:
            Path to the image to read.

    Returns:
        A list of text results found by EasyOCR.

    Raises:
        FileNotFoundError:
            Raised when the image file cannot be found.
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
    Draw OCR results on the image and save them.

    For each text item:
    - Draw a box around the text.
    - Write the recognized text on the image.
    - Show the confidence score next to the text.

    Args:
        image_path:
            Path to the original image.
        results:
            OCR results returned by EasyOCR.
        output_path:
            Path where the result image will be saved.

    Raises:
        FileNotFoundError:
            Raised when the image file cannot be found or read.
        IOError:
            Raised when the result image cannot be saved.
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
