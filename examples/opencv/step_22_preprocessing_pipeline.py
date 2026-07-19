from pathlib import Path

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)
from src.preprocessing.pipeline import (
    preprocess_for_ocr,
)


def main() -> None:
    """
    Tam OCR preprocessing pipeline kullanımını örnekler.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_path = Path(
        "results/preprocessing/pipeline/"
        "medicine_sample_final_preprocessed.jpg"
    )

    # Orijinal görüntüyü oku.
    image = read_image(
        image_path
    )

    print("\n===== OCR PREPROCESSING PIPELINE =====")
    print(f"Orijinal Shape: {image.shape}")

    # Tüm preprocessing adımlarını tek fonksiyonla uygula.
    processed_image = preprocess_for_ocr(
        image=image,
        resize_width=1600,
        crop_region=None,
        median_kernel_size=5,
        clahe_clip_limit=2.0,
        clahe_tile_grid_size=(8, 8),
        adaptive_block_size=11,
        adaptive_constant=2,
        morphology_kernel_size=(3, 3),
    )

    print(
        f"İşlenmiş Shape: "
        f"{processed_image.shape}"
    )

    print(
        f"İşlenmiş ndim: "
        f"{processed_image.ndim}"
    )

    print(
        f"Minimum piksel değeri: "
        f"{processed_image.min()}"
    )

    print(
        f"Maksimum piksel değeri: "
        f"{processed_image.max()}"
    )

    # Son OCR görüntüsünü kaydet.
    save_image(
        processed_image,
        output_path,
    )

    print(
        f"\nFinal preprocessing görüntüsü kaydedildi: "
        f"{output_path}"
    )

    # Orijinal görüntüyü sadece gösterim için küçült.
    original_preview = resize_image(
        image,
        width=800,
    )

    # İşlenmiş görüntüyü sadece gösterim için küçült.
    processed_preview = resize_image(
        processed_image,
        width=800,
    )

    print(
        "\nÖnce orijinal görüntü gösterilecektir."
    )

    display_image(
        original_preview,
        window_name="Original Image",
    )

    print(
        "Şimdi OCR için hazırlanmış görüntü "
        "gösterilecektir."
    )

    display_image(
        processed_preview,
        window_name="Final OCR Preprocessed Image",
    )


if __name__ == "__main__":
    main()