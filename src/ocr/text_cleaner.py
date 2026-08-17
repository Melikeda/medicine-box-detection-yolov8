import re
from typing import Any


def clean_text(
    text: str,
) -> str:
    """
    Clean a single text value found by OCR.

    Operations performed:
    - Convert line breaks to spaces.
    - Collapse repeated spaces into one.
    - Remove leading and trailing spaces.
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
    Extract only cleaned text values from EasyOCR results.

    Results with confidence below minimum_confidence are excluded from the list.
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
    Combine a list of text values into a single text value.
    """
    cleaned_texts = [
        clean_text(text)
        for text in texts
        if clean_text(text)
    ]

    return separator.join(cleaned_texts)
