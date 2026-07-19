from pathlib import Path

import cv2
import numpy as np

from src.ocr.ocr_reader import (
    create_ocr_reader,
    read_text_from_image,
)


def print_ocr_results(
    title: str,
    results: list,
) -> None:
    """
    OCR sonuçlarını terminale düzenli şekilde yazdırır.
    """
    print(f"\n{title}")
    print("-" * 60)

    if not results:
        print("Herhangi bir metin bulunamadı.")
        return

    for index, result in enumerate(results, start=1):
        _, text, confidence = result

        print(
            f"{index}. {text} "
            f"| Güven: {confidence:.4f}"
        )


def apply_clahe(
    grayscale_image: np.ndarray,
) -> np.ndarray:
    """
    Grayscale görüntünün yerel kontrastını CLAHE ile artırır.
    """
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )

    return clahe.apply(grayscale_image)


def apply_sharpening(
    image: np.ndarray,
) -> np.ndarray:
    """
    Görüntüdeki harf kenarlarını hafifçe keskinleştirir.
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
        ddepth=-1,
        kernel=sharpening_kernel,
    )


def main() -> None:
    input_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_directory = Path(
        "results/ocr/preprocessing"
    )

    grayscale_path = output_directory / "grayscale.jpg"
    resized_path = output_directory / "resized_2x.jpg"
    clahe_path = output_directory / "clahe.jpg"
    sharpened_path = output_directory / "clahe_sharpened.jpg"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Görüntü bulunamadı: {input_path}"
        )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    image = cv2.imread(str(input_path))

    if image is None:
        raise FileNotFoundError(
            f"Görüntü OpenCV ile okunamadı: {input_path}"
        )

    grayscale_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    resized_image = cv2.resize(
        grayscale_image,
        None,
        fx=2.0,
        fy=2.0,
        interpolation=cv2.INTER_CUBIC,
    )

    clahe_image = apply_clahe(
        resized_image
    )

    sharpened_image = apply_sharpening(
        clahe_image
    )

    images_to_save = {
        grayscale_path: grayscale_image,
        resized_path: resized_image,
        clahe_path: clahe_image,
        sharpened_path: sharpened_image,
    }

    for output_path, output_image in images_to_save.items():
        save_success = cv2.imwrite(
            str(output_path),
            output_image,
        )

        if not save_success:
            raise IOError(
                f"Görüntü kaydedilemedi: {output_path}"
            )

    print("OCR okuyucusu hazırlanıyor...")

    reader = create_ocr_reader(
        languages=["tr", "en"],
        use_gpu=False,
    )

    print("Orijinal görüntü OCR ile okunuyor...")
    original_results = read_text_from_image(
        reader=reader,
        image_path=input_path,
    )

    print("Grayscale görüntü OCR ile okunuyor...")
    grayscale_results = read_text_from_image(
        reader=reader,
        image_path=grayscale_path,
    )

    print("2 kat büyütülmüş görüntü OCR ile okunuyor...")
    resized_results = read_text_from_image(
        reader=reader,
        image_path=resized_path,
    )

    print("CLAHE uygulanmış görüntü OCR ile okunuyor...")
    clahe_results = read_text_from_image(
        reader=reader,
        image_path=clahe_path,
    )

    print("CLAHE + sharpening görüntüsü OCR ile okunuyor...")
    sharpened_results = read_text_from_image(
        reader=reader,
        image_path=sharpened_path,
    )

    print_ocr_results(
        title="ORİJİNAL GÖRÜNTÜ OCR SONUÇLARI",
        results=original_results,
    )

    print_ocr_results(
        title="GRAYSCALE OCR SONUÇLARI",
        results=grayscale_results,
    )

    print_ocr_results(
        title="2 KAT BÜYÜTÜLMÜŞ OCR SONUÇLARI",
        results=resized_results,
    )

    print_ocr_results(
        title="CLAHE OCR SONUÇLARI",
        results=clahe_results,
    )

    print_ocr_results(
        title="CLAHE + SHARPENING OCR SONUÇLARI",
        results=sharpened_results,
    )

    print(
        "\nİşlenmiş görüntüler kaydedildi: "
        f"{output_directory}"
    )


if __name__ == "__main__":
    main()