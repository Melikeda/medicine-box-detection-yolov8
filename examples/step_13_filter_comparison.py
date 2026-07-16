from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.preprocessing.basic_operations import (
    read_image,
    save_image,
)
from src.preprocessing.color_operations import (
    convert_to_grayscale,
)
from src.preprocessing.filter_operations import (
    apply_bilateral_filter,
    apply_gaussian_blur,
    apply_median_blur,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)


def add_salt_and_pepper_noise(
    image,
    noise_ratio: float = 0.03,
    random_seed: int = 42,
):
    """
    Görüntüye yapay salt-and-pepper gürültüsü ekler.

    Salt:
        Bazı pikselleri beyaz, yani 255 yapar.

    Pepper:
        Bazı pikselleri siyah, yani 0 yapar.

    Args:
        image: Gürültü eklenecek grayscale görüntü.
        noise_ratio: Gürültülü hale getirilecek piksel oranı.
            Örneğin 0.03, piksellerin yaklaşık yüzde 3'üdür.
        random_seed: Aynı sonucun tekrar üretilebilmesi için seed.

    Returns:
        Salt-and-pepper gürültüsü eklenmiş görüntü.
    """

    if image.ndim != 2:
        raise ValueError(
            "Salt-and-pepper örneği için grayscale görüntü gereklidir."
        )

    if not 0 < noise_ratio < 1:
        raise ValueError(
            "noise_ratio değeri 0 ile 1 arasında olmalıdır."
        )

    noisy_image = image.copy()

    rng = np.random.default_rng(random_seed)

    total_pixels = image.size
    noisy_pixel_count = int(total_pixels * noise_ratio)

    # Gürültünün yarısını beyaz, yarısını siyah yap.
    salt_count = noisy_pixel_count // 2
    pepper_count = noisy_pixel_count - salt_count

    # Beyaz yapılacak rastgele koordinatlar.
    salt_y = rng.integers(
        0,
        image.shape[0],
        size=salt_count,
    )

    salt_x = rng.integers(
        0,
        image.shape[1],
        size=salt_count,
    )

    noisy_image[salt_y, salt_x] = 255

    # Siyah yapılacak rastgele koordinatlar.
    pepper_y = rng.integers(
        0,
        image.shape[0],
        size=pepper_count,
    )

    pepper_x = rng.integers(
        0,
        image.shape[1],
        size=pepper_count,
    )

    noisy_image[pepper_y, pepper_x] = 0

    return noisy_image


def show_image(
    image,
    title: str,
) -> None:
    """
    Tek bir grayscale görüntüyü Matplotlib ile gösterir.
    """

    plt.figure(figsize=(10, 6))
    plt.imshow(
        image,
        cmap="gray",
        vmin=0,
        vmax=255,
    )
    plt.title(title)
    plt.axis("off")
    plt.show()


def main() -> None:
    """
    Gaussian, Median ve Bilateral filtreleri
    salt-and-pepper gürültüsü üzerinde karşılaştırır.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_directory = Path(
        "results/preprocessing/filter_comparison"
    )

    # Görüntüyü oku ve grayscale'e dönüştür.
    image = read_image(image_path)

    grayscale_image = convert_to_grayscale(
        image
    )

    # İşlemleri hızlandırmak ve görsel karşılaştırmayı
    # kolaylaştırmak için görüntüyü küçült.
    grayscale_image = resize_image(
        grayscale_image,
        width=800,
    )

    # Görüntüye yapay salt-and-pepper noise ekle.
    noisy_image = add_salt_and_pepper_noise(
        grayscale_image,
        noise_ratio=0.03,
        random_seed=42,
    )

    # Aynı gürültülü görüntüye üç farklı filtre uygula.
    gaussian_image = apply_gaussian_blur(
        noisy_image,
        kernel_size=(5, 5),
        sigma=0,
    )

    median_image = apply_median_blur(
        noisy_image,
        kernel_size=5,
    )

    bilateral_image = apply_bilateral_filter(
        noisy_image,
        diameter=9,
        sigma_color=75,
        sigma_space=75,
    )

    print("\n===== FILTER COMPARISON =====")

    print(f"Grayscale shape : {grayscale_image.shape}")
    print(f"Noisy shape     : {noisy_image.shape}")
    print(f"Gaussian shape  : {gaussian_image.shape}")
    print(f"Median shape    : {median_image.shape}")
    print(f"Bilateral shape : {bilateral_image.shape}")

    print("\nSalt-and-pepper gürültü oranı: %3")
    print("Tüm filtreler aynı gürültülü görüntüye uygulanmıştır.")

    # Sonuçları ayrı dosyalar halinde kaydet.
    save_image(
        grayscale_image,
        output_directory / "01_grayscale.jpg",
    )

    save_image(
        noisy_image,
        output_directory / "02_salt_and_pepper_noise.jpg",
    )

    save_image(
        gaussian_image,
        output_directory / "03_gaussian_blur.jpg",
    )

    save_image(
        median_image,
        output_directory / "04_median_blur.jpg",
    )

    save_image(
        bilateral_image,
        output_directory / "05_bilateral_filter.jpg",
    )

    print(
        "\nKarşılaştırma görüntüleri kaydedildi: "
        f"{output_directory}"
    )

    # Görüntüleri sırayla göster.
    show_image(
        grayscale_image,
        "1 - Original Grayscale Image",
    )

    show_image(
        noisy_image,
        "2 - Salt and Pepper Noise",
    )

    show_image(
        gaussian_image,
        "3 - Gaussian Blur",
    )

    show_image(
        median_image,
        "4 - Median Blur",
    )

    show_image(
        bilateral_image,
        "5 - Bilateral Filter",
    )


if __name__ == "__main__":
    main()