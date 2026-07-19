from pathlib import Path
from typing import Any

import cv2
import easyocr
import numpy as np


def preprocess_image_for_ocr(
    image_path: str | Path,
    scale_factor: float = 2.0,
) -> np.ndarray:
    """
    OCR öncesinde görüntüyü işler.

    İşlem sırası:
    1. Görüntüyü oku
    2. Grayscale
    3. Resize
    4. CLAHE
    5. Sharpening
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Görüntü bulunamadı: {image_path}"
        )

    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(
            f"Görüntü OpenCV ile okunamadı: {image_path}"
        )

    grayscale_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    resized_image = cv2.resize(
        grayscale_image,
        None,
        fx=scale_factor,
        fy=scale_factor,
        interpolation=cv2.INTER_CUBIC,
    )

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )

    clahe_image = clahe.apply(
        resized_image
    )

    sharpening_kernel = np.array(
        [
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0],
        ],
        dtype=np.float32,
    )

    sharpened_image = cv2.filter2D(
        clahe_image,
        ddepth=-1,
        kernel=sharpening_kernel,
    )

    return sharpened_image


def run_ocr_pipeline(
    reader: easyocr.Reader,
    image_path: str | Path,
    save_preprocessed_image: bool = False,
    output_path: str | Path | None = None,
) -> list[Any]:
    """
    Görüntüyü işler ve OCR sonucunu döndürür.
    """
    processed_image = preprocess_image_for_ocr(
        image_path=image_path,
    )

    if save_preprocessed_image:
        if output_path is None:
            raise ValueError(
                "save_preprocessed_image=True olduğunda "
                "output_path verilmelidir."
            )

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        success = cv2.imwrite(
            str(output_path),
            processed_image,
        )

        if not success:
            raise IOError(
                f"İşlenmiş görüntü kaydedilemedi: "
                f"{output_path}"
            )

    results = reader.readtext(
        processed_image
    )

    return results