from pathlib import Path
from typing import Any

import cv2
import numpy as np

from src.ocr.ocr_reader import create_ocr_reader
from src.ocr.text_cleaner import (
    combine_texts,
    extract_texts,
)


INPUT_IMAGE_PATH = Path(
    "results/integration/yolo_ocr/"
    "aferin_forte_yolo_crop_upscaled.jpg"
)

OUTPUT_DIRECTORY = Path(
    "results/integration/multi_preprocessing_ocr"
)

MINIMUM_CONFIDENCE = 0.0


def print_separator(
    title: str,
    separator_length: int = 70,
) -> None:
    """
    Terminalde başlık ve ayırıcı çizgi gösterir.
    """
    print(f"\n{title}")
    print("-" * separator_length)


def validate_input_path() -> None:
    """
    Girdi görselinin mevcut olup olmadığını kontrol eder.
    """
    if not INPUT_IMAGE_PATH.exists():
        raise FileNotFoundError(
            "Büyütülmüş YOLO crop bulunamadı: "
            f"{INPUT_IMAGE_PATH}\n"
            "Önce step_07_yolo_crop_ocr dosyasını çalıştır."
        )


def load_image(
    image_path: Path,
) -> np.ndarray:
    """
    Görseli OpenCV ile okur.
    """
    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise ValueError(
            f"Görsel okunamadı: {image_path}"
        )

    return image


def convert_to_grayscale(
    image: np.ndarray,
) -> np.ndarray:
    """
    BGR görüntüyü gri tonlamaya dönüştürür.
    """
    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )


def apply_clahe(
    grayscale_image: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: tuple[int, int] = (8, 8),
) -> np.ndarray:
    """
    Görüntünün yerel kontrastını artırır.

    CLAHE, özellikle aydınlatmanın görüntünün farklı
    bölgelerinde değiştiği durumlarda yararlıdır.
    """
    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=tile_grid_size,
    )

    return clahe.apply(
        grayscale_image
    )


def apply_gaussian_blur(
    grayscale_image: np.ndarray,
) -> np.ndarray:
    """
    Görüntüdeki küçük gürültüleri azaltır.
    """
    return cv2.GaussianBlur(
        grayscale_image,
        (3, 3),
        0,
    )


def apply_otsu_threshold(
    grayscale_image: np.ndarray,
) -> np.ndarray:
    """
    Otsu yöntemi ile otomatik eşik değeri belirleyerek
    siyah-beyaz görüntü oluşturur.
    """
    blurred_image = apply_gaussian_blur(
        grayscale_image
    )

    _, threshold_image = cv2.threshold(
        blurred_image,
        0,
        255,
        cv2.THRESH_BINARY
        + cv2.THRESH_OTSU,
    )

    return threshold_image


def apply_adaptive_threshold(
    grayscale_image: np.ndarray,
) -> np.ndarray:
    """
    Görüntünün farklı bölgeleri için farklı eşik değerleri
    kullanarak siyah-beyaz görüntü oluşturur.
    """
    blurred_image = apply_gaussian_blur(
        grayscale_image
    )

    return cv2.adaptiveThreshold(
        blurred_image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )


def apply_sharpening(
    image: np.ndarray,
) -> np.ndarray:
    """
    Kenarları ve yazıları daha belirgin hâle getirir.
    """
    sharpening_kernel = np.array(
        [
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0],
        ],
        dtype=np.float32,
    )

    return cv2.filter2D(
        image,
        -1,
        sharpening_kernel,
    )


def apply_unsharp_mask(
    image: np.ndarray,
) -> np.ndarray:
    """
    Görüntünün bulanık bir kopyasını kullanarak
    detayları ve yazı kenarlarını güçlendirir.
    """
    blurred_image = cv2.GaussianBlur(
        image,
        (0, 0),
        sigmaX=2.0,
    )

    sharpened_image = cv2.addWeighted(
        image,
        1.8,
        blurred_image,
        -0.8,
        0,
    )

    return sharpened_image


def create_preprocessing_variants(
    image: np.ndarray,
) -> dict[str, np.ndarray]:
    """
    OCR ile test edilecek farklı görüntü
    ön işleme varyantlarını oluşturur.
    """
    grayscale_image = convert_to_grayscale(
        image
    )

    clahe_image = apply_clahe(
        grayscale_image
    )

    variants: dict[str, np.ndarray] = {
        "01_original_color": image,
        "02_grayscale": grayscale_image,
        "03_clahe": clahe_image,
        "04_sharpened_color": apply_sharpening(
            image
        ),
        "05_sharpened_clahe": apply_sharpening(
            clahe_image
        ),
        "06_unsharp_mask": apply_unsharp_mask(
            image
        ),
        "07_otsu_threshold": apply_otsu_threshold(
            clahe_image
        ),
        "08_adaptive_threshold": (
            apply_adaptive_threshold(
                clahe_image
            )
        ),
    }

    return variants


def save_variant(
    variant_name: str,
    image: np.ndarray,
) -> Path:
    """
    Ön işleme varyantını dosyaya kaydeder.
    """
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIRECTORY
        / f"{variant_name}.jpg"
    )

    save_success = cv2.imwrite(
        str(output_path),
        image,
    )

    if not save_success:
        raise IOError(
            f"Görüntü kaydedilemedi: {output_path}"
        )

    return output_path


def run_easyocr(
    reader: Any,
    image: np.ndarray,
) -> list[Any]:
    """
    Belirtilen görüntü üzerinde EasyOCR çalıştırır.

    detail=1 kullanıldığı için sonuçlarda:
    - koordinatlar
    - metin
    - güven skoru

    bilgileri bulunur.
    """
    results = reader.readtext(
        image,
        detail=1,
        paragraph=False,
    )

    return results


def calculate_average_confidence(
    ocr_results: list[Any],
) -> float:
    """
    OCR sonuçlarının ortalama güven skorunu hesaplar.
    """
    confidence_values: list[float] = []

    for result in ocr_results:
        if len(result) < 3:
            continue

        confidence = float(
            result[2]
        )

        confidence_values.append(
            confidence
        )

    if not confidence_values:
        return 0.0

    return sum(
        confidence_values
    ) / len(
        confidence_values
    )


def print_ocr_results(
    variant_name: str,
    ocr_results: list[Any],
) -> None:
    """
    Bir ön işleme varyantının OCR sonuçlarını
    terminalde gösterir.
    """
    print_separator(
        f"OCR Varyantı: {variant_name}"
    )

    if not ocr_results:
        print("Metin bulunamadı.")
        return

    for index, result in enumerate(
        ocr_results,
        start=1,
    ):
        if len(result) < 3:
            continue

        _, text, confidence = result

        print(
            f"{index}. {text} "
            f"(güven: {float(confidence):.2f})"
        )

    extracted_texts = extract_texts(
        ocr_results=ocr_results,
        minimum_confidence=MINIMUM_CONFIDENCE,
    )

    combined_text = combine_texts(
        texts=extracted_texts,
    )

    average_confidence = (
        calculate_average_confidence(
            ocr_results
        )
    )

    print(
        "\nBirleştirilmiş metin:"
    )

    if combined_text:
        print(combined_text)
    else:
        print("Birleştirilecek metin bulunamadı.")

    print(
        "\nOrtalama OCR güven skoru: "
        f"{average_confidence:.2f}"
    )


def print_summary(
    summary_results: list[
        tuple[str, str, float]
    ],
) -> None:
    """
    Tüm ön işleme varyantlarının sonuçlarını
    özet olarak gösterir.
    """
    print_separator(
        "Çoklu Ön İşleme OCR Özeti",
        separator_length=80,
    )

    sorted_results = sorted(
        summary_results,
        key=lambda result: result[2],
        reverse=True,
    )

    for index, (
        variant_name,
        combined_text,
        average_confidence,
    ) in enumerate(
        sorted_results,
        start=1,
    ):
        print(
            f"\n{index}. {variant_name}"
        )

        print(
            "   Ortalama güven: "
            f"{average_confidence:.2f}"
        )

        print(
            f"   Metin: {combined_text}"
        )


def main() -> None:
    """
    Aynı YOLO crop üzerinde farklı ön işleme
    yöntemlerini deneyerek OCR sonuçlarını karşılaştırır.
    """
    validate_input_path()

    print(
        "\nÇoklu Ön İşleme ve OCR Karşılaştırması"
    )
    print("=" * 70)

    print(
        f"Girdi görseli: {INPUT_IMAGE_PATH}"
    )

    print(
        f"Çıktı klasörü: {OUTPUT_DIRECTORY}"
    )

    image = load_image(
        image_path=INPUT_IMAGE_PATH,
    )

    print(
        f"Görsel boyutu: {image.shape}"
    )

    preprocessing_variants = (
        create_preprocessing_variants(
            image=image,
        )
    )

    print(
        "Oluşturulan varyant sayısı: "
        f"{len(preprocessing_variants)}"
    )

    reader = create_ocr_reader(
        languages=["tr", "en"],
        use_gpu=False,
    )

    summary_results: list[
        tuple[str, str, float]
    ] = []

    for variant_name, variant_image in (
        preprocessing_variants.items()
    ):
        variant_output_path = save_variant(
            variant_name=variant_name,
            image=variant_image,
        )

        print(
            f"\nVaryant kaydedildi: "
            f"{variant_output_path}"
        )

        ocr_results = run_easyocr(
            reader=reader,
            image=variant_image,
        )

        print_ocr_results(
            variant_name=variant_name,
            ocr_results=ocr_results,
        )

        extracted_texts = extract_texts(
            ocr_results=ocr_results,
            minimum_confidence=(
                MINIMUM_CONFIDENCE
            ),
        )

        combined_text = combine_texts(
            texts=extracted_texts,
        )

        average_confidence = (
            calculate_average_confidence(
                ocr_results
            )
        )

        summary_results.append(
            (
                variant_name,
                combined_text,
                average_confidence,
            )
        )

    print_summary(
        summary_results=summary_results,
    )

    print_separator(
        "Test Tamamlandı"
    )

    print(
        "Tüm ön işleme varyantları OCR ile test edildi."
    )

    print(
        "Özellikle Aferin kelimesinin hangi varyantta "
        "daha doğru okunduğunu kontrol et."
    )


if __name__ == "__main__":
    main()