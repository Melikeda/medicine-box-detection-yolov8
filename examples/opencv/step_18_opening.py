from pathlib import Path

import numpy as np

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
    apply_opening,
)
from src.preprocessing.threshold_operations import (
    apply_adaptive_threshold,
)


def add_white_noise(
    image,
    noise_ratio: float = 0.01,
    random_seed: int = 42,
):
    """
    Binary görüntüye küçük beyaz gürültü noktaları ekler.

    Opening işleminin etkisini daha net göstermek için
    rastgele seçilen bazı pikseller beyaz yapılır.
    """

    if image.ndim != 2:
        raise ValueError(
            "Bu örnek için tek kanallı görüntü gereklidir."
        )

    if not 0 < noise_ratio < 1:
        raise ValueError(
            "noise_ratio değeri 0 ile 1 arasında olmalıdır."
        )

    noisy_image = image.copy()

    rng = np.random.default_rng(random_seed)

    noise_count = int(
        image.size * noise_ratio
    )

    noise_y = rng.integers(
        0,
        image.shape[0],
        size=noise_count,
    )

    noise_x = rng.integers(
        0,
        image.shape[1],
        size=noise_count,
    )

    noisy_image[noise_y, noise_x] = 255

    return noisy_image


def main() -> None:
    """
    Opening işleminin küçük beyaz gürültüler üzerindeki
    etkisini örnekler.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_directory = Path(
        "results/preprocessing/opening_comparison"
    )

    image = read_image(image_path)

    grayscale_image = convert_to_grayscale(
        image
    )

    clahe_image = apply_clahe(
        grayscale_image,
        clip_limit=2.0,
        tile_grid_size=(8, 8),
    )

    threshold_image = apply_adaptive_threshold(
        grayscale_image=clahe_image,
        max_value=255,
        block_size=11,
        constant=2,
    )

    # Opening etkisini daha net göstermek için
    # binary görüntüye yapay beyaz noktalar ekle.
    noisy_image = add_white_noise(
        threshold_image,
        noise_ratio=0.01,
        random_seed=42,
    )

    opening_3x3 = apply_opening(
        noisy_image,
        kernel_size=(3, 3),
        iterations=1,
    )

    opening_5x5 = apply_opening(
        noisy_image,
        kernel_size=(5, 5),
        iterations=1,
    )

    print("\n===== OPENING COMPARISON =====")

    print(f"Noisy Shape      : {noisy_image.shape}")
    print(f"Opening 3x3 Shape: {opening_3x3.shape}")
    print(f"Opening 5x5 Shape: {opening_5x5.shape}")

    print("\n3x3 kernel → Daha hafif gürültü temizleme")
    print("5x5 kernel → Daha güçlü gürültü temizleme")

    save_image(
        noisy_image,
        output_directory / "01_white_noise.jpg",
    )

    save_image(
        opening_3x3,
        output_directory / "02_opening_3x3.jpg",
    )

    save_image(
        opening_5x5,
        output_directory / "03_opening_5x5.jpg",
    )

    print(
        "\nKarşılaştırma görüntüleri kaydedildi: "
        f"{output_directory}"
    )

    noisy_preview = resize_image(
        noisy_image,
        width=800,
    )

    opening_3x3_preview = resize_image(
        opening_3x3,
        width=800,
    )

    opening_5x5_preview = resize_image(
        opening_5x5,
        width=800,
    )

    print("\nÖnce beyaz gürültülü görüntü gösterilecektir.")

    display_image(
        noisy_preview,
        window_name="White Noise Image",
    )

    print("Şimdi 3x3 Opening görüntüsü gösterilecektir.")

    display_image(
        opening_3x3_preview,
        window_name="Opening - 3x3 Kernel",
    )

    print("Şimdi 5x5 Opening görüntüsü gösterilecektir.")

    display_image(
        opening_5x5_preview,
        window_name="Opening - 5x5 Kernel",
    )


if __name__ == "__main__":
    main()