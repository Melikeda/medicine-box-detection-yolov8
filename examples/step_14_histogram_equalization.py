from pathlib import Path

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.color_operations import (
    apply_histogram_equalization,
    convert_to_grayscale,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)


def main() -> None:
    """
    Grayscale görüntüye Histogram Equalization uygular
    ve işlem öncesi-sonrası görüntüleri karşılaştırır.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_path = Path(
        "results/preprocessing/"
        "medicine_sample_histogram_equalization.jpg"
    )

    # Renkli görüntüyü oku.
    image = read_image(image_path)

    # Histogram Equalization tek kanallı görüntü beklediği için
    # görüntüyü önce grayscale biçimine dönüştür.
    grayscale_image = convert_to_grayscale(
        image
    )

    # Global kontrast artırma işlemini uygula.
    equalized_image = apply_histogram_equalization(
        grayscale_image
    )

    print("\n===== HISTOGRAM EQUALIZATION INFORMATION =====")

    print(f"Grayscale Shape : {grayscale_image.shape}")
    print(f"Equalized Shape : {equalized_image.shape}")

    print(f"Grayscale ndim  : {grayscale_image.ndim}")
    print(f"Equalized ndim  : {equalized_image.ndim}")

    print(
        f"Grayscale minimum piksel değeri: "
        f"{grayscale_image.min()}"
    )

    print(
        f"Grayscale maksimum piksel değeri: "
        f"{grayscale_image.max()}"
    )

    print(
        f"Equalized minimum piksel değeri: "
        f"{equalized_image.min()}"
    )

    print(
        f"Equalized maksimum piksel değeri: "
        f"{equalized_image.max()}"
    )

    # Kontrastı artırılmış görüntüyü kaydet.
    save_image(
        equalized_image,
        output_path,
    )

    print(
        f"\nHistogram Equalization görüntüsü kaydedildi: "
        f"{output_path}"
    )

    # Büyük görüntüleri yalnızca gösterim amacıyla küçült.
    grayscale_preview = resize_image(
        grayscale_image,
        width=800,
    )

    equalized_preview = resize_image(
        equalized_image,
        width=800,
    )

    print("\nÖnce grayscale görüntü gösterilecektir.")

    display_image(
        grayscale_preview,
        window_name="Grayscale Image",
    )

    print(
        "Şimdi Histogram Equalization görüntüsü "
        "gösterilecektir."
    )

    display_image(
        equalized_preview,
        window_name="Histogram Equalization Image",
    )


if __name__ == "__main__":
    main()