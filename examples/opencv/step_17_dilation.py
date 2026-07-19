from pathlib import Path

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.color_operations import (
    apply_clahe,
    convert_to_grayscale,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)
from src.preprocessing.morphological_operations import (
    apply_dilation,
)
from src.preprocessing.threshold_operations import (
    apply_adaptive_threshold,
)


def main() -> None:
    """
    Farklı kernel boyutlarının Dilation sonucuna etkisini karşılaştırır.

    Karşılaştırılan görüntüler:
        1. Adaptive Threshold görüntüsü
        2. 3x3 kernel ile Dilation
        3. 7x7 kernel ile Dilation
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_directory = Path(
        "results/preprocessing/dilation_comparison"
    )

    # Renkli görüntüyü oku.
    image = read_image(image_path)

    # Görüntüyü grayscale biçimine dönüştür.
    grayscale_image = convert_to_grayscale(
        image
    )

    # Yerel kontrastı artır.
    clahe_image = apply_clahe(
        grayscale_image,
        clip_limit=2.0,
        tile_grid_size=(8, 8),
    )

    # Morfolojik işlemi daha net görebilmek için
    # binary görüntü oluştur.
    threshold_image = apply_adaptive_threshold(
        grayscale_image=clahe_image,
        max_value=255,
        block_size=11,
        constant=2,
    )

    # Küçük kernel ile hafif Dilation uygula.
    dilation_3x3 = apply_dilation(
        threshold_image,
        kernel_size=(3, 3),
        iterations=1,
    )

    # Büyük kernel ile daha güçlü Dilation uygula.
    dilation_7x7 = apply_dilation(
        threshold_image,
        kernel_size=(7, 7),
        iterations=1,
    )

    print("\n===== DILATION COMPARISON =====")

    print(f"Threshold Shape : {threshold_image.shape}")
    print(f"3x3 Shape       : {dilation_3x3.shape}")
    print(f"7x7 Shape       : {dilation_7x7.shape}")

    print("\n3x3 kernel → Daha hafif genişletme")
    print("7x7 kernel → Daha güçlü genişletme")

    # Sonuçları kaydet.
    save_image(
        threshold_image,
        output_directory / "01_threshold.jpg",
    )

    save_image(
        dilation_3x3,
        output_directory / "02_dilation_3x3.jpg",
    )

    save_image(
        dilation_7x7,
        output_directory / "03_dilation_7x7.jpg",
    )

    print(
        "\nKarşılaştırma görüntüleri kaydedildi: "
        f"{output_directory}"
    )

    # Büyük görüntüleri yalnızca gösterim için küçült.
    threshold_preview = resize_image(
        threshold_image,
        width=800,
    )

    dilation_3x3_preview = resize_image(
        dilation_3x3,
        width=800,
    )

    dilation_7x7_preview = resize_image(
        dilation_7x7,
        width=800,
    )

    print("\nÖnce Threshold görüntüsü gösterilecektir.")

    display_image(
        threshold_preview,
        window_name="Adaptive Threshold Image",
    )

    print("Şimdi 3x3 Dilation görüntüsü gösterilecektir.")

    display_image(
        dilation_3x3_preview,
        window_name="Dilation - 3x3 Kernel",
    )

    print("Şimdi 7x7 Dilation görüntüsü gösterilecektir.")

    display_image(
        dilation_7x7_preview,
        window_name="Dilation - 7x7 Kernel",
    )


if __name__ == "__main__":
    main()