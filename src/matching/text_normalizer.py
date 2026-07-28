"""OCR metinlerini eşleştirme öncesi normalize eder."""

OCR_CONFUSABLE_TRANSLATION = str.maketrans(
    {
        "€": "c",
        "©": "c",
        "¢": "c",
    }
)


def normalize_ocr_text(text: str) -> str:
    """
    OCR çıktısını karşılaştırma için standart biçime dönüştürür.

    Sık OCR hatalarını düzeltir (ör. € → c, Ibucold C kutularında).
    """
    cleaned = text.strip().casefold().translate(
        OCR_CONFUSABLE_TRANSLATION
    )
    return " ".join(cleaned.split())
