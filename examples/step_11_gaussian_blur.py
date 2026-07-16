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
    apply_gaussian_blur,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)


def main() -> None:
    """
    Gaussian Blur kullanımını örnekler.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_path = Path(
        "results/preprocessing/medicine_sample_gaussian_blur.jpg"
    )

    # Görüntüyü oku.
    image = read_image(image_path)

    # Önce grayscale'e dönüştür.
    grayscale_image = convert_to_grayscale(
        image
    )

    # Gaussian Blur uygula.
    blurred_image = apply_gaussian_blur(
        grayscale_image,
        kernel_size=(5, 5),
        sigma=0,
    )

    print("\n===== GAUSSIAN BLUR INFORMATION =====")

    print(f"Grayscale Shape : {grayscale_image.shape}")
    print(f"Blur Shape      : {blurred_image.shape}")

    print(f"Grayscale ndim  : {grayscale_image.ndim}")
    print(f"Blur ndim       : {blurred_image.ndim}")

    print(f"İlk piksel (Gray): {grayscale_image[0,0]}")
    print(f"İlk piksel (Blur): {blurred_image[0,0]}")

    save_image(
        blurred_image,
        output_path,
    )

    print(
        f"\nBlur görüntüsü kaydedildi: "
        f"{output_path}"
    )

    grayscale_preview = resize_image(
        grayscale_image,
        width=800,
    )

    blurred_preview = resize_image(
        blurred_image,
        width=800,
    )

    print("\nÖnce grayscale görüntü gösterilecektir.")

    display_image(
        grayscale_preview,
        window_name="Grayscale Image",
    )

    print("Şimdi Gaussian Blur görüntüsü gösterilecektir.")

    display_image(
        blurred_preview,
        window_name="Gaussian Blur Image",
    )


if __name__ == "__main__":
    main()