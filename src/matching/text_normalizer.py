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


def is_garbage_ocr_text(text: str) -> bool:
    """
    Anlamsiz OCR gurultusunu tespit eder.

    Ornek: 1778v1 7dv~ ww 6w oc / bw od7
    """
    normalized = normalize_ocr_text(text)

    if not normalized:
        return True

    compact = normalized.replace(" ", "")
    alpha_count = sum(character.isalpha() for character in compact)
    digit_count = sum(character.isdigit() for character in compact)
    special_count = sum(
        not character.isalnum() for character in compact
    )

    if alpha_count < 3:
        return True

    total = len(compact)
    if total == 0:
        return True

    if digit_count > 0 and digit_count / total >= 0.2:
        return True

    if special_count > 0 and alpha_count / total < 0.65:
        return True

    words = normalized.split()
    if len(words) >= 3:
        noisy_words = sum(
            1
            for word in words
            if any(character.isdigit() for character in word)
            and sum(character.isalpha() for character in word) < 4
        )
        if noisy_words >= 2:
            return True

    return False
