from pathlib import Path

import cv2
import matplotlib.pyplot as plt

from src.ocr.experimental.paddle_ocr_reader import (
    create_paddle_ocr_reader,
)


def resize_for_display(
    image,
    width: int = 900,
):
    """
    BÃ¼yÃ¼k gÃ¶rseli ekranda rahat gÃ¶stermek iÃ§in kÃ¼Ã§Ã¼ltÃ¼r.
    """
    original_height, original_width = image.shape[:2]

    scale = width / original_width
    new_height = int(original_height * scale)

    return cv2.resize(
        image,
        (width, new_height),
        interpolation=cv2.INTER_AREA,
    )


def main() -> None:
    input_path = Path(
        "data/samples/aferin_forte.jpg"
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"GÃ¶rsel bulunamadÄ±: {input_path}"
        )

    image = cv2.imread(str(input_path))

    if image is None:
        raise ValueError(
            f"GÃ¶rsel okunamadÄ±: {input_path}"
        )

    print("Orijinal gÃ¶rsel boyutu:", image.shape)

    display_image = resize_for_display(
        image=image,
        width=900,
    )

    display_rgb = cv2.cvtColor(
        display_image,
        cv2.COLOR_BGR2RGB,
    )

    plt.figure(figsize=(12, 8))
    plt.imshow(display_rgb)
    plt.title("A-Ferin Forte GÃ¶rseli")
    plt.axis("on")
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
