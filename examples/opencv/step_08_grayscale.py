from pathlib import Path

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.color_operations import (
    convert_to_grayscale,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)


def main() -> None:
    """
    Renkli bir görüntüyü grayscale görüntüye dönüştürmeyi örnekler.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_path = Path(
        "results/preprocessing/medicine_sample_grayscale.jpg"
    )

    # Renkli görüntüyü oku.
    image = read_image(image_path)

    # Görüntüyü grayscale biçimine dönüştür.
    grayscale_image = convert_to_grayscale(image)

    print("\n===== GRAYSCALE INFORMATION =====")

    print(f"Renkli görüntü shape    : {image.shape}")
    print(f"Grayscale görüntü shape : {grayscale_image.shape}")

    print(f"Renkli görüntü ndim     : {image.ndim}")
    print(f"Grayscale görüntü ndim  : {grayscale_image.ndim}")

    print(f"Renkli ilk piksel       : {image[0, 0]}")
    print(f"Grayscale ilk piksel    : {grayscale_image[0, 0]}")

    # Grayscale görüntüyü diske kaydet.
    save_image(
        grayscale_image,
        output_path,
    )

    print(f"\nGrayscale görüntü kaydedildi: {output_path}")

    # Büyük renkli görüntüyü yalnızca gösterim için küçült.
    color_preview = resize_image(
        image,
        width=800,
    )

    # Grayscale görüntüyü yalnızca gösterim için küçült.
    grayscale_preview = resize_image(
        grayscale_image,
        width=800,
    )

    print("\nÖnce renkli görüntü gösterilecektir.")

    display_image(
        color_preview,
        window_name="Original Color Image",
    )

    print("Şimdi grayscale görüntü gösterilecektir.")

    display_image(
        grayscale_preview,
        window_name="Grayscale Image",
    )


if __name__ == "__main__":
    main()