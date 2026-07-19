from pathlib import Path

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.color_operations import (
    convert_to_grayscale,
)
from src.preprocessing.filter_operations import (
    apply_median_blur,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)


def main() -> None:
    """
    Median Blur kullanımını örnekler.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_path = Path(
        "results/preprocessing/medicine_sample_median_blur.jpg"
    )

    # Görüntüyü oku.
    image = read_image(image_path)

    # Önce grayscale'e dönüştür.
    grayscale_image = convert_to_grayscale(
        image
    )

    # Median Blur uygula.
    blurred_image = apply_median_blur(
        grayscale_image,
        kernel_size=5,
    )

    print("\n===== MEDIAN BLUR INFORMATION =====")

    print(f"Grayscale Shape : {grayscale_image.shape}")
    print(f"Blur Shape      : {blurred_image.shape}")

    print(f"Grayscale ndim  : {grayscale_image.ndim}")
    print(f"Blur ndim       : {blurred_image.ndim}")

    print(f"İlk piksel (Gray): {grayscale_image[0, 0]}")
    print(f"İlk piksel (Blur): {blurred_image[0, 0]}")

    save_image(
        blurred_image,
        output_path,
    )

    print(
        f"\nMedian Blur görüntüsü kaydedildi: "
        f"{output_path}"
    )

    # Büyük görüntüleri yalnızca gösterim için küçült.
    grayscale_preview = resize_image(
        grayscale_image,
        width=800,
    )

    median_preview = resize_image(
        blurred_image,
        width=800,
    )

    print("\nÖnce grayscale görüntü gösterilecektir.")

    display_image(
        grayscale_preview,
        window_name="Grayscale Image",
    )

    print("Şimdi Median Blur görüntüsü gösterilecektir.")

    display_image(
        median_preview,
        window_name="Median Blur Image",
    )


if __name__ == "__main__":
    main()