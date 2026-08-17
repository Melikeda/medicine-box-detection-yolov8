"""
Compare blur and sharpening filters side by side.

Run:
    python -m examples.preprocessing.step_13_filter_comparison
"""

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
    Adds synthetic salt-and-pepper noise to an image.

    Salt:
        Sets some pixels to white, meaning 255.

    Pepper:
        Sets some pixels to black, meaning 0.

    Args:
        image: Grayscale image to receive noise.
        noise_ratio: Ratio of pixels to make noisy.
            For example, 0.03 is roughly 3 percent of the pixels.
        random_seed: Seed for reproducible output.

    Returns:
        Image with salt-and-pepper noise applied.
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

    # Make half of the noise white and half black.
    salt_count = noisy_pixel_count // 2
    pepper_count = noisy_pixel_count - salt_count

    # Random coordinates to set to white.
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

    # Random coordinates to set to black.
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
    Displays a single grayscale image with Matplotlib.
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
    Compares Gaussian, Median, and Bilateral filters
    on salt-and-pepper noise.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_directory = Path(
        "results/preprocessing/filter_comparison"
    )

    # Read the image and convert it to grayscale.
    image = read_image(image_path)

    grayscale_image = convert_to_grayscale(
        image
    )

    # Shrink the image to speed up processing and
    # make visual comparison easier.
    grayscale_image = resize_image(
        grayscale_image,
        width=800,
    )

    # Add synthetic salt-and-pepper noise to the image.
    noisy_image = add_salt_and_pepper_noise(
        grayscale_image,
        noise_ratio=0.03,
        random_seed=42,
    )

    # Apply three different filters to the same noisy image.
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

    # Save the results as separate files.
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

    # Display the images in sequence.
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
