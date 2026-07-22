from pathlib import Path
from typing import Any

import cv2
import numpy as np

from src.ocr.ocr_reader import create_ocr_reader
from src.ocr.text_cleaner import clean_text


INPUT_DIRECTORY = Path(
    "results/integration/multi_preprocessing_ocr"
)

SELECTED_VARIANTS = [
    "01_original_color.jpg",
    "04_sharpened_color.jpg",
    "06_unsharp_mask.jpg",
    "07_otsu_threshold.jpg",
]

MINIMUM_CONFIDENCE = 0.05


def print_separator(
    title: str,
    separator_length: int = 70,
) -> None:
    """
    Terminalde başlık ve ayırıcı çizgi gösterir.
    """
    print(f"\n{title}")
    print("-" * separator_length)


def validate_variant_paths() -> list[Path]:
    """
    Seçilen OCR varyantlarının mevcut olduğunu kontrol eder.
    """
    variant_paths: list[Path] = []

    for filename in SELECTED_VARIANTS:
        variant_path = INPUT_DIRECTORY / filename

        if not variant_path.exists():
            raise FileNotFoundError(
                f"OCR varyantı bulunamadı: {variant_path}"
            )

        variant_paths.append(
            variant_path
        )

    return variant_paths


def load_image(
    image_path: Path,
) -> np.ndarray:
    """
    Görüntüyü OpenCV ile okur.
    """
    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_UNCHANGED,
    )

    if image is None:
        raise ValueError(
            f"Görüntü okunamadı: {image_path}"
        )

    return image


def run_ocr(
    reader: Any,
    image: np.ndarray,
) -> list[Any]:
    """
    Görüntü üzerinde EasyOCR çalıştırır.
    """
    return reader.readtext(
        image,
        detail=1,
        paragraph=False,
    )


def normalize_candidate(
    text: str,
) -> str:
    """
    OCR adayını karşılaştırmaya uygun hâle getirir.

    İşlemler:
    - Metni temizler.
    - Küçük harfe çevirir.
    - Köşeli parantez gibi OCR artıklarını kaldırır.
    - Tireleri boşluğa dönüştürür.
    - Fazla boşlukları temizler.
    """
    normalized_text = clean_text(
        text
    ).lower()

    replacement_characters = [
        "[",
        "]",
        "{",
        "}",
        "(",
        ")",
        "|",
    ]

    for character in replacement_characters:
        normalized_text = normalized_text.replace(
            character,
            "",
        )

    normalized_text = normalized_text.replace(
        "-",
        " ",
    )

    normalized_text = clean_text(
        normalized_text
    )

    return normalized_text


def extract_candidates(
    ocr_results: list[Any],
    minimum_confidence: float,
) -> list[tuple[str, float]]:
    """
    EasyOCR sonuçlarından metin ve güven
    skoru çiftlerini çıkarır.
    """
    candidates: list[tuple[str, float]] = []

    for result in ocr_results:
        if len(result) < 3:
            continue

        _, text, confidence = result

        confidence = float(
            confidence
        )

        if confidence < minimum_confidence:
            continue

        normalized_text = normalize_candidate(
            text
        )

        if not normalized_text:
            continue

        candidates.append(
            (
                normalized_text,
                confidence,
            )
        )

    return candidates


def create_adjacent_candidates(
    candidates: list[tuple[str, float]],
) -> list[tuple[str, float]]:
    """
    Yan yana bulunan OCR parçalarını birleştirerek
    yeni adaylar oluşturur.

    Örnek:
        A + ferin → aferin
    """
    combined_candidates: list[
        tuple[str, float]
    ] = []

    for index in range(
        len(candidates) - 1
    ):
        first_text, first_confidence = (
            candidates[index]
        )

        second_text, second_confidence = (
            candidates[index + 1]
        )

        joined_text = (
            first_text.replace(" ", "")
            + second_text.replace(" ", "")
        )

        combined_confidence = (
            first_confidence
            + second_confidence
        ) / 2

        combined_candidates.append(
            (
                joined_text,
                combined_confidence,
            )
        )

    return combined_candidates


def remove_duplicate_candidates(
    candidates: list[tuple[str, float]],
) -> list[tuple[str, float]]:
    """
    Aynı metne sahip adaylardan en yüksek güvenli
    olanı korur.
    """
    best_candidates: dict[str, float] = {}

    for text, confidence in candidates:
        current_confidence = best_candidates.get(
            text,
            -1.0,
        )

        if confidence > current_confidence:
            best_candidates[text] = confidence

    sorted_candidates = sorted(
        best_candidates.items(),
        key=lambda candidate: candidate[1],
        reverse=True,
    )

    return sorted_candidates


def is_possible_medicine_name(
    text: str,
) -> bool:
    """
    OCR adayının ilaç adı olabilecek genel yapıda
    olup olmadığını kontrol eder.

    Bu fonksiyon yalnızca çok kısa, tamamen sayısal
    veya doz bilgisine benzeyen adayları eler.
    """
    compact_text = text.replace(
        " ",
        ""
    )

    if len(compact_text) < 4:
        return False

    if compact_text.isdigit():
        return False

    dosage_terms = {
        "mg",
        "ml",
        "tablet",
        "kapsül",
        "kapsul",
        "film",
        "kaplı",
        "kapli",
    }

    if compact_text in dosage_terms:
        return False

    return any(
        character.isalpha()
        for character in compact_text
    )


def print_variant_results(
    variant_name: str,
    candidates: list[tuple[str, float]],
) -> None:
    """
    Bir varyanttan çıkarılan OCR adaylarını gösterir.
    """
    print_separator(
        f"Varyant: {variant_name}"
    )

    for index, (
        text,
        confidence,
    ) in enumerate(
        candidates,
        start=1,
    ):
        print(
            f"{index}. {text} "
            f"(güven: {confidence:.2f})"
        )


def main() -> None:
    """
    Seçilen preprocessing varyantlarının OCR
    sonuçlarını birleştirerek ortak aday havuzu üretir.
    """
    variant_paths = validate_variant_paths()

    print(
        "\nÇoklu OCR Aday Birleştirme"
    )
    print("=" * 70)

    reader = create_ocr_reader(
        languages=["tr", "en"],
        use_gpu=False,
    )

    all_candidates: list[
        tuple[str, float]
    ] = []

    for variant_path in variant_paths:
        image = load_image(
            image_path=variant_path,
        )

        ocr_results = run_ocr(
            reader=reader,
            image=image,
        )

        candidates = extract_candidates(
            ocr_results=ocr_results,
            minimum_confidence=MINIMUM_CONFIDENCE,
        )

        adjacent_candidates = (
            create_adjacent_candidates(
                candidates=candidates,
            )
        )

        variant_candidates = (
            candidates
            + adjacent_candidates
        )

        print_variant_results(
            variant_name=variant_path.stem,
            candidates=variant_candidates,
        )

        all_candidates.extend(
            variant_candidates
        )

    unique_candidates = (
        remove_duplicate_candidates(
            candidates=all_candidates,
        )
    )

    medicine_name_candidates = [
        (
            text,
            confidence,
        )
        for text, confidence in unique_candidates
        if is_possible_medicine_name(text)
    ]

    print_separator(
        "Birleştirilmiş İlaç Adı Adayları"
    )

    for index, (
        text,
        confidence,
    ) in enumerate(
        medicine_name_candidates,
        start=1,
    ):
        print(
            f"{index}. {text} "
            f"(güven: {confidence:.2f})"
        )

    print_separator(
        "Aday Birleştirme Tamamlandı"
    )

    print(
        "Bir sonraki adımda bu adaylar "
        "RapidFuzz ilaç eşleştiricisine gönderilecek."
    )


if __name__ == "__main__":
    main()