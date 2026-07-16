from pathlib import Path

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.color_operations import (
    convert_to_grayscale,
)
from src.preprocessing.edge_operations import (
    apply_canny_edge_detection,
)
from src.preprocessing.filter_operations import (
    apply_gaussian_blur,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)


def main() -> None:
    """
    Canny Edge Detection kullanımını örnekler.

    İşlem sırası:

        Original Image
                ↓
        Grayscale
                ↓
        Gaussian Blur
                ↓
        Canny Edge Detection
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_path = Path(
        "results/preprocessing/medicine_sample_edges.jpg"
    )

    # --------------------------------------------------
    # Görüntüyü oku
    # --------------------------------------------------

    image = read_image(
        image_path
    )

    # --------------------------------------------------
    # Grayscale'e dönüştür
    # --------------------------------------------------

    grayscale_image = convert_to_grayscale(
        image
    )

    # --------------------------------------------------
    # Gaussian Blur uygula
    # Amaç:
    # Küçük gürültüleri azaltarak
    # Canny'nin gereksiz kenar bulmasını önlemek.
    # --------------------------------------------------

    blurred_image = apply_gaussian_blur(
        grayscale_image,
        kernel_size=(5, 5),
        sigma=0,
    )

    # --------------------------------------------------
    # Canny Edge Detection uygula
    # --------------------------------------------------

    edge_image = apply_canny_edge_detection(
        blurred_image,
        threshold1=100,
        threshold2=200,
    )

    print("\n===== EDGE DETECTION INFORMATION =====")

    print(f"Blur Shape  : {blurred_image.shape}")
    print(f"Edge Shape  : {edge_image.shape}")

    print(f"Blur ndim   : {blurred_image.ndim}")
    print(f"Edge ndim   : {edge_image.ndim}")

    print(f"Minimum Pixel : {edge_image.min()}")
    print(f"Maximum Pixel : {edge_image.max()}")

    # --------------------------------------------------
    # Sonucu kaydet
    # --------------------------------------------------

    save_image(
        edge_image,
        output_path,
    )

    print(
        f"\nEdge görüntüsü kaydedildi:\n{output_path}"
    )

    # --------------------------------------------------
    # Büyük görüntüyü yalnızca gösterim için küçült
    # --------------------------------------------------

    blur_preview = resize_image(
        blurred_image,
        width=800,
    )

    edge_preview = resize_image(
        edge_image,
        width=800,
    )

    print("\nÖnce Blur görüntüsü gösterilecektir.")

    display_image(
        blur_preview,
        window_name="Gaussian Blur Image",
    )

    print("Şimdi Edge görüntüsü gösterilecektir.")

    display_image(
        edge_preview,
        window_name="Canny Edge Detection",
    )


if __name__ == "__main__":
    main()