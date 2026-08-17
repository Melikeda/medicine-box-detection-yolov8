"""Normalize OCR text before matching."""

OCR_CONFUSABLE_TRANSLATION = str.maketrans(
    {
        "€": "c",
        "©": "c",
        "¢": "c",
        "®": " ",
        "™": " ",
    }
)


def normalize_ocr_text(text: str) -> str:
    """
    Convert OCR output to a standard form for comparison.

    Fix common OCR mistakes, for example euro-like symbols to c on Ibucold C boxes.
    """
    cleaned = text.strip().casefold().translate(
        OCR_CONFUSABLE_TRANSLATION
    )
    return " ".join(cleaned.split())


def is_garbage_ocr_text(text: str) -> bool:
    """
    Detect meaningless OCR noise.

    Example: 1778v1 7dv~ ww 6w oc / bw od7
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
