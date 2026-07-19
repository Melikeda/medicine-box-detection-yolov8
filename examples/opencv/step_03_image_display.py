from pathlib import Path

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
)


def main() -> None:
    """
    Okunan görüntünün OpenCV penceresinde gösterilmesini örnekler.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    image = read_image(image_path)

    print("Görüntü penceresini kapatmak için herhangi bir tuşa bas.")

    display_image(
        image,
        window_name="Medicine Sample - Original Image"
    )


if __name__ == "__main__":
    main()