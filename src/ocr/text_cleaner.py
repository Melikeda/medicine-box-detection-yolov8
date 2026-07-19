import re
from typing import Any


def clean_text(
    text: str,
) -> str:
    """
    OCR tarafından bulunan tek bir metni temizler.

    Yapılan işlemler:
    - Satır sonlarını boşluğa çevirir.
    - Birden fazla boşluğu teke indirir.
    - Metnin başındaki ve sonundaki boşlukları kaldırır.
    """
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def extract_texts(
    ocr_results: list[Any],
    minimum_confidence: float = 0.0,
) -> list[str]:
    """
    EasyOCR sonuçlarından yalnızca temizlenmiş metinleri çıkarır.

    Güven skoru minimum_confidence değerinden düşük olan
    sonuçlar listeye alınmaz.
    """
    extracted_texts: list[str] = []

    for result in ocr_results:
        _, text, confidence = result

        if confidence < minimum_confidence:
            continue

        cleaned_text = clean_text(text)

        if cleaned_text:
            extracted_texts.append(cleaned_text)

    return extracted_texts


def combine_texts(
    texts: list[str],
    separator: str = " ",
) -> str:
    """
    Metin listesini tek bir metin hâline getirir.
    """
    cleaned_texts = [
        clean_text(text)
        for text in texts
        if clean_text(text)
    ]

    return separator.join(cleaned_texts)