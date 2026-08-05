from src.matching.medicine_matcher import (
    calculate_medicine_score,
    is_dosage_or_form_only_text,
    is_generic_active_ingredient,
    is_generic_single_word,
)
from src.matching.text_normalizer import normalize_ocr_text
from src.services.config import (
    IGNORED_OCR_PHRASES,
    MEDICINE_NAME_SUFFIXES,
)


def normalize_filter_text(text: str) -> str:
    """OCR adayını filtreleme için standart biçime dönüştürür."""
    return normalize_ocr_text(text)


def contains_letter(text: str) -> bool:
    """Metnin en az bir alfabetik karakter içerip içermediğini kontrol eder."""
    return any(character.isalpha() for character in text)


def is_single_alphabetic_word(text: str) -> bool:
    """Metnin yalnızca harflerden oluşan tek kelime olup olmadığını kontrol eder."""
    normalized_text = normalize_filter_text(text)
    return (
        " " not in normalized_text
        and normalized_text.isalpha()
    )


def is_valid_base_name_candidate(text: str) -> bool:
    """OCR metninin ilaç adının ana parçası olarak uygun olup olmadığını kontrol eder."""
    normalized_text = normalize_filter_text(text)

    if not normalized_text:
        return False

    if not is_single_alphabetic_word(normalized_text):
        return False

    if not 3 <= len(normalized_text) <= 20:
        return False

    if normalized_text in MEDICINE_NAME_SUFFIXES:
        return False

    if normalized_text in IGNORED_OCR_PHRASES:
        return False

    if is_generic_single_word(normalized_text):
        return False

    if is_generic_active_ingredient(normalized_text):
        return False

    return True


ACTIVE_INGREDIENT_SUFFIXES = frozenset(
    {
        "ol",
        "hcl",
        "maleat",
        "sodyum",
        "potasyum",
        "hidroklorur",
        "sulfat",
        "fosfat",
    }
)


def is_likely_active_ingredient(text: str) -> bool:
    """Uzun kimyasal/etken madde metinlerini marka adından ayırır."""
    normalized_text = normalize_filter_text(text)

    if not is_single_alphabetic_word(normalized_text):
        return False

    if is_generic_active_ingredient(normalized_text):
        return True

    if len(normalized_text) <= 8:
        return False

    return any(
        normalized_text.endswith(suffix)
        for suffix in ACTIVE_INGREDIENT_SUFFIXES
    )


def select_brand_name_candidate(
    candidate_texts: list[str],
) -> str | None:
    """Marka adına benzeyen en kısa geçerli OCR adayını seçer."""
    brand_like_candidates = [
        text
        for text in candidate_texts
        if is_valid_base_name_candidate(text)
        and not is_likely_active_ingredient(text)
    ]

    if not brand_like_candidates:
        return None

    return min(
        brand_like_candidates,
        key=lambda text: len(normalize_filter_text(text)),
    )


def create_medicine_name_candidates(
    candidate_texts: list[str],
) -> list[str]:
    """
    OCR aday parçalarından tam ilaç adı adayları üretir.

    Örnek: aferin + forte → aferin forte
    """
    normalized_candidates: list[str] = []
    seen_normalized_candidates: set[str] = set()

    for text in candidate_texts:
        normalized_text = normalize_filter_text(text)

        if not normalized_text:
            continue

        if normalized_text in seen_normalized_candidates:
            continue

        seen_normalized_candidates.add(normalized_text)
        normalized_candidates.append(normalized_text)

    suffix_candidates = [
        text
        for text in normalized_candidates
        if text in MEDICINE_NAME_SUFFIXES
    ]

    single_letter_suffixes = [
        text
        for text in normalized_candidates
        if len(text) == 1 and text.isalpha()
    ]

    base_candidates = [
        text
        for text in normalized_candidates
        if is_valid_base_name_candidate(text)
    ]

    generated_candidates: list[str] = []
    seen_all_candidates: set[str] = set(normalized_candidates)

    for base_candidate in base_candidates:
        for suffix_candidate in suffix_candidates:
            combined_candidate = (
                f"{base_candidate} {suffix_candidate}"
            )

            if combined_candidate in seen_all_candidates:
                continue

            seen_all_candidates.add(combined_candidate)
            generated_candidates.append(combined_candidate)

        for letter_suffix in single_letter_suffixes:
            combined_candidate = (
                f"{base_candidate} {letter_suffix}"
            )

            if combined_candidate in seen_all_candidates:
                continue

            seen_all_candidates.add(combined_candidate)
            generated_candidates.append(combined_candidate)

    return normalized_candidates + generated_candidates


def count_alphabetic_characters(text: str) -> int:
    """Metindeki alfabetik karakter sayısını döndürür."""
    return sum(character.isalpha() for character in text)


def is_valid_matching_candidate(
    text: str,
    *,
    minimum_text_length: int = 3,
) -> bool:
    """OCR adayının ilaç adı eşleştirmesinde kullanılmaya uygun olup olmadığını kontrol eder."""
    normalized_text = normalize_filter_text(text)

    if not normalized_text:
        return False

    if not contains_letter(normalized_text):
        return False

    if count_alphabetic_characters(normalized_text) < minimum_text_length:
        return False

    if normalized_text in IGNORED_OCR_PHRASES:
        return False

    if is_generic_single_word(normalized_text):
        return False

    if is_generic_active_ingredient(normalized_text):
        return False

    if is_dosage_or_form_only_text(normalized_text):
        return False

    dosage_markers = {"mg", "ml", "mcg", "gr"}
    words = normalized_text.split()

    if any(marker in words for marker in dosage_markers):
        return False

    digit_count = sum(
        character.isdigit() for character in normalized_text
    )
    letter_count = sum(
        character.isalpha() for character in normalized_text
    )

    if digit_count > letter_count:
        return False

    return True


def filter_candidate_texts(
    candidate_texts: list[str],
    *,
    minimum_text_length: int = 3,
) -> list[str]:
    """RapidFuzz eşleştirmesi öncesinde OCR adaylarını temizler."""
    filtered_texts: list[str] = []
    seen_texts: set[str] = set()

    for text in candidate_texts:
        normalized_text = normalize_filter_text(text)

        if not is_valid_matching_candidate(
            normalized_text,
            minimum_text_length=minimum_text_length,
        ):
            continue

        if normalized_text in seen_texts:
            continue

        seen_texts.add(normalized_text)
        filtered_texts.append(normalized_text)

    return filtered_texts


MatchRecord = tuple[dict[str, str], float, str]


def rank_medicine_matches(
    candidate_texts: list[str],
    medicines: list[dict[str, str]],
    top_count: int = 3,
) -> list[MatchRecord]:
    """
    Her OCR adayını her ilaç adıyla karşılaştırır ve en iyi eşleşmeleri döndürür.
    """
    if top_count <= 0:
        raise ValueError("top_count sıfırdan büyük olmalıdır.")

    best_matches_by_medicine: dict[str, MatchRecord] = {}

    for candidate_text in candidate_texts:
        for medicine in medicines:
            score, medicine_name = calculate_medicine_score(
                query_text=candidate_text,
                medicine=medicine,
            )

            if medicine_name is None:
                continue

            medicine_id = medicine.get(
                "medicine_id",
                medicine_name,
            )

            current_match = best_matches_by_medicine.get(
                medicine_id
            )

            should_update = (
                current_match is None
                or score > current_match[1]
                or (
                    score == current_match[1]
                    and len(candidate_text) > len(current_match[2])
                )
            )

            if should_update:
                best_matches_by_medicine[medicine_id] = (
                    medicine,
                    score,
                    candidate_text,
                )

    ranked_matches = sorted(
        best_matches_by_medicine.values(),
        key=lambda match: (
            match[1],
            len(match[2]),
            len(match[0].get("medicine_name", "")),
        ),
        reverse=True,
    )

    return ranked_matches[:top_count]
