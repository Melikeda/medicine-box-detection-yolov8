from pathlib import Path

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)


def main() -> None:
    """
    Görüntüyü yeniden boyutlandırmayı örnekler.
    """

    # Giriş görüntüsünün yolu.
    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    # Çıktı görüntüsünün yolu.
    output_path = Path(
        "results/preprocessing/medicine_sample_resized.jpg"
    )

    # Görüntüyü oku.
    image = read_image(image_path)

    # Görüntüyü genişliği 800 piksel olacak şekilde yeniden boyutlandır.
    resized_image = resize_image(
        image=image,
        width=800
    )

    print("\n===== RESIZE INFORMATION =====")

    print(f"Orijinal Shape : {image.shape}")
    print(f"Yeni Shape     : {resized_image.shape}")

    # Yeniden boyutlandırılan görüntüyü kaydet.
    save_image(
        resized_image,
        output_path
    )

    print(f"\nGörüntü kaydedildi: {output_path}")

    # Yeniden boyutlandırılan görüntüyü göster.
    display_image(
        resized_image,
        window_name="Resized Image"
    )


if __name__ == "__main__":
    main()