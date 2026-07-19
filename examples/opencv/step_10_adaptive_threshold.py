from pathlib import Path

import numpy as np

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
from src.preprocessing.threshold_operations import (
    apply_adaptive_threshold,
    apply_binary_threshold,
)


def main() -> None:
    """
    Binary threshold ve adaptive threshold sonuçlarını karşılaştırır.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    binary_output_path = Path(
        "results/preprocessing/medicine_sample_binary_threshold.jpg"
    )

    adaptive_output_path = Path(
        "results/preprocessing/medicine_sample_adaptive_threshold.jpg"
    )

    # Renkli görüntüyü oku.
    image = read_image(image_path)

    # Threshold işlemleri tek kanallı görüntü beklediği için
    # görüntüyü önce grayscale biçimine dönüştür.
    grayscale_image = convert_to_grayscale(image)

    # Tüm görüntü için tek bir eşik değeri kullan.
    used_threshold, binary_threshold_image = apply_binary_threshold(
        grayscale_image=grayscale_image,
        threshold_value=127,
        max_value=255,
    )

    # Her yerel bölge için farklı eşik değeri hesapla.
    adaptive_threshold_image = apply_adaptive_threshold(
        grayscale_image=grayscale_image,
        max_value=255,
        block_size=11,
        constant=2,
    )

    print("\n===== ADAPTIVE THRESHOLD INFORMATION =====")

    print(f"Binary threshold değeri : {used_threshold}")
    print(f"Grayscale shape         : {grayscale_image.shape}")
    print(f"Binary threshold shape  : {binary_threshold_image.shape}")
    print(f"Adaptive threshold shape: {adaptive_threshold_image.shape}")

    print(
        "Binary piksel değerleri  : "
        f"{np.unique(binary_threshold_image)}"
    )

    print(
        "Adaptive piksel değerleri: "
        f"{np.unique(adaptive_threshold_image)}"
    )

    # Sonuçları diske kaydet.
    save_image(
        binary_threshold_image,
        binary_output_path,
    )

    save_image(
        adaptive_threshold_image,
        adaptive_output_path,
    )

    print(
        f"\nBinary threshold görüntüsü kaydedildi: "
        f"{binary_output_path}"
    )

    print(
        f"Adaptive threshold görüntüsü kaydedildi: "
        f"{adaptive_output_path}"
    )

    # Büyük görüntüleri yalnızca gösterim için küçült.
    grayscale_preview = resize_image(
        grayscale_image,
        width=800,
    )

    binary_preview = resize_image(
        binary_threshold_image,
        width=800,
    )

    adaptive_preview = resize_image(
        adaptive_threshold_image,
        width=800,
    )

    print("\nÖnce grayscale görüntü gösterilecektir.")

    display_image(
        grayscale_preview,
        window_name="Grayscale Image",
    )

    print("Şimdi binary threshold görüntüsü gösterilecektir.")

    display_image(
        binary_preview,
        window_name="Binary Threshold Image",
    )

    print("Şimdi adaptive threshold görüntüsü gösterilecektir.")

    display_image(
        adaptive_preview,
        window_name="Adaptive Threshold Image",
    )


if __name__ == "__main__":
    main()