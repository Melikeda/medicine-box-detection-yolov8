from rapidfuzz import fuzz

from src.matching.text_normalizer import normalize_ocr_text


DEFAULT_SCORE_CUTOFF = 88.0


GENERIC_SINGLE_WORDS = {
    "fort",
    "forte",
    "plus",
    "extra",
    "cold",
    "flu",
    "tablet",
    "film",
    "kapli",
    "kaplı",
    "kapsul",
    "kapsül",
    "capsule",
    "surup",
    "şurup",
    "suspension",
}

# Common active ingredients that cannot select a brand when read alone by OCR.
GENERIC_ACTIVE_INGREDIENTS = frozenset(
    {
        "ibuprofen",
        "paracetamol",
        "parasetamol",
        "diclofenac",
        "naproxen",
        "dexketoprofen",
        "flurbiprofen",
        "codeine",
        "aspirin",
        "metamizol",
        "tramadol",
    }
)

ACTIVE_INGREDIENT_ONLY_NAME_SCORE_LIMIT = 65.0


def normalize_text(
    text: str,
) -> str:
    """
    Clean text for comparison.

    Removes case differences and trims leading and trailing whitespace.
    """
    return normalize_ocr_text(text)


def is_generic_single_word(
    text: str,
) -> bool:
    """
    Check whether the OCR text is a generic word that should not select
    a medicine on its own.

    Example:
        forte
        plus
        cold
        tablet
    """
    normalized_text = normalize_text(text)

    if not normalized_text:
        return False

    words = normalized_text.split()

    if len(words) != 1:
        return False

    return normalized_text in GENERIC_SINGLE_WORDS


def is_generic_active_ingredient(text: str) -> bool:
    """
    Return True when OCR contains only a common active ingredient name.

    Example: ibuprofen cannot distinguish Nurofen from Brufen.
    """
    normalized_text = normalize_text(text)
    words = normalized_text.split()

    if len(words) != 1:
        return False

    return normalized_text in GENERIC_ACTIVE_INGREDIENTS


def is_active_ingredient_only_match(
    query_text: str,
    medicine: dict[str, str],
    match_score: float,
    *,
    name_score_limit: float = ACTIVE_INGREDIENT_ONLY_NAME_SCORE_LIMIT,
) -> bool:
    """
    Detect whether the match comes only from the active_ingredient field.

    Prevents selecting the wrong product when there is no brand or product-name signal.
    """
    if match_score < DEFAULT_SCORE_CUTOFF:
        return False

    active_ingredient = medicine.get("active_ingredient", "").strip()

    if (
        not active_ingredient
        or active_ingredient.upper().startswith("VERIFY_FROM_OFFICIAL")
    ):
        return False

    ingredient_score = calculate_text_similarity(
        query_text=query_text,
        medicine_name=active_ingredient,
    )

    if ingredient_score < match_score - 0.5:
        return False

    for field_name in ("medicine_name", "brand_name"):
        field_value = medicine.get(field_name, "").strip()

        if not field_value:
            continue

        field_score = calculate_text_similarity(
            query_text=query_text,
            medicine_name=field_value,
        )

        if field_score >= name_score_limit:
            return False

    return True


def _looks_like_brand_word(word: str) -> bool:
    """Check whether an OCR fragment looks like part of a brand name."""
    normalized_word = normalize_text(word)

    if not normalized_word or " " in normalized_word:
        return False

    if not normalized_word.isalpha():
        return False

    if not 3 <= len(normalized_word) <= 20:
        return False

    if is_generic_single_word(normalized_word):
        return False

    return True


def is_dosage_or_form_only_text(text: str) -> bool:
    """
    Return True when OCR output contains only dosage or form information.

    Example: "250 mo / j0o mo tablot" has no brand name and is excluded from matching.
    """
    from src.services.config import DOSAGE_FORM_MARKERS

    normalized_text = normalize_text(text)

    if not any(character.isdigit() for character in normalized_text):
        return False

    tokenized_text = normalized_text.replace("/", " ")
    words = tokenized_text.split()

    has_dosage_marker = any(
        word in DOSAGE_FORM_MARKERS
        or any(
            marker in word
            for marker in DOSAGE_FORM_MARKERS
        )
        for word in words
    )

    if not has_dosage_marker:
        return False

    def _is_brand_token(word: str) -> bool:
        if word in DOSAGE_FORM_MARKERS:
            return False

        if any(marker in word for marker in DOSAGE_FORM_MARKERS):
            return False

        return _looks_like_brand_word(word)

    has_brand_word = any(
        _is_brand_token(word) for word in words
    )

    return not has_brand_word


def get_medicine_name(
    medicine: dict[str, str],
) -> str | None:
    """
    Return the cleaned medicine_name value from a medicine record.

    Return None when medicine_name is empty.
    """
    medicine_name = medicine.get(
        "medicine_name",
        "",
    ).strip()

    if not medicine_name:
        return None

    return medicine_name


def calculate_text_similarity(
    query_text: str,
    medicine_name: str,
) -> float:
    """
    Calculate the similarity score between OCR text and the medicine full name.

    The score ranges from 0 to 100.
    """
    cleaned_query = normalize_text(
        query_text
    )

    cleaned_medicine_name = normalize_text(
        medicine_name
    )

    if not cleaned_query:
        return 0.0

    if not cleaned_medicine_name:
        return 0.0

    score = fuzz.WRatio(
        cleaned_query,
        cleaned_medicine_name,
    )

    return float(score)


def calculate_medicine_score(
    query_text: str,
    medicine: dict[str, str],
) -> tuple[float, str | None]:
    """
    Compare OCR text with medicine_name, brand_name, and active_ingredient fields.

    Return the highest score; the matched record is represented by medicine_name.
    """
    medicine_name = get_medicine_name(medicine)

    if medicine_name is None:
        return 0.0, None

    best_score = 0.0
    skip_active_ingredient = is_dosage_or_form_only_text(
        query_text
    )

    fields_to_compare = ["medicine_name", "brand_name"]

    if not skip_active_ingredient:
        fields_to_compare.append("active_ingredient")

    for field_name in fields_to_compare:
        field_value = medicine.get(field_name, "").strip()

        if not field_value:
            continue

        if field_value.upper().startswith("VERIFY_FROM_OFFICIAL"):
            continue

        score = calculate_text_similarity(
            query_text=query_text,
            medicine_name=field_value,
        )

        if score > best_score:
            best_score = score

    return best_score, medicine_name


def find_best_medicine_match(
    query_text: str,
    medicines: list[dict[str, str]],
    score_cutoff: float = DEFAULT_SCORE_CUTOFF,
) -> tuple[
    dict[str, str] | None,
    float,
    str | None,
]:
    """
    Find the best medicine match in the database for a single OCR text.

    Matching uses only the medicine_name field.

    Generic words cannot select a medicine on their own.

    Returns:
        (
            matched medicine record,
            match score,
            matched medicine_name
        )
    """
    cleaned_query = query_text.strip()

    if not cleaned_query:
        return None, 0.0, None

    if is_generic_single_word(cleaned_query):
        return None, 0.0, None

    if is_generic_active_ingredient(cleaned_query):
        return None, 0.0, None

    best_medicine: dict[str, str] | None = None
    best_score = 0.0
    best_medicine_name: str | None = None

    from src.matching.brand_disambiguation import (
        evidence_alignment_boost,
        is_base_sku,
    )

    for medicine in medicines:
        score, medicine_name = (
            calculate_medicine_score(
                query_text=cleaned_query,
                medicine=medicine,
            )
        )

        if medicine_name is None:
            continue

        if is_active_ingredient_only_match(
            query_text=cleaned_query,
            medicine=medicine,
            match_score=score,
        ):
            continue

        is_higher_score = score > best_score
        is_same_score = score == best_score

        # Same score: avoid letting longer names such as Plus/Gargara/Jel win by default.
        # Prefer the base SKU when OCR evidence does not support the variant.
        should_replace = is_higher_score
        if is_same_score and best_medicine is not None:
            current_boost = evidence_alignment_boost(
                medicine,
                cleaned_query,
            )
            best_boost = evidence_alignment_boost(
                best_medicine,
                cleaned_query,
            )
            if current_boost > best_boost:
                should_replace = True
            elif current_boost == best_boost:
                current_base = is_base_sku(medicine)
                best_base = is_base_sku(best_medicine)
                if current_base and not best_base:
                    should_replace = True
                elif current_base == best_base:
                    # Esitlikte daha kisa / markaya yakin isim
                    if len(medicine_name) < len(
                        best_medicine_name or medicine_name
                    ):
                        should_replace = True

        if should_replace:
            best_medicine = medicine
            best_score = score
            best_medicine_name = medicine_name

    if best_score < score_cutoff:
        return (
            None,
            best_score,
            best_medicine_name,
        )

    return (
        best_medicine,
        best_score,
        best_medicine_name,
    )


def find_best_match_from_texts(
    texts: list[str],
    medicines: list[dict[str, str]],
    score_cutoff: float = DEFAULT_SCORE_CUTOFF,
) -> tuple[
    dict[str, str] | None,
    float,
    str | None,
]:
    """
    Find the best medicine match across multiple OCR texts.

    Generic words are not evaluated on their own.

    When scores are tied, prefer the longer OCR text and the more specific medicine name.

    Returns:
        (
            matched medicine record,
            match score,
            best OCR text
        )
    """
    best_medicine: dict[str, str] | None = None
    best_score = 0.0
    best_ocr_text: str | None = None
    best_medicine_name: str | None = None

    for text in texts:
        cleaned_text = text.strip()

        if not cleaned_text:
            continue

        if is_generic_single_word(cleaned_text):
            continue

        if is_generic_active_ingredient(cleaned_text):
            continue

        (
            medicine,
            score,
            medicine_name,
        ) = find_best_medicine_match(
            query_text=cleaned_text,
            medicines=medicines,
            score_cutoff=0.0,
        )

        if medicine is None:
            continue

        is_higher_score = score > best_score

        is_same_score = score == best_score

        is_longer_ocr_text = (
            best_ocr_text is None
            or len(cleaned_text)
            > len(best_ocr_text)
        )

        is_more_specific_medicine = (
            best_medicine_name is None
            or (
                medicine_name is not None
                and len(medicine_name)
                > len(best_medicine_name)
            )
        )

        should_update = is_higher_score or (
            is_same_score
            and (
                is_longer_ocr_text
                or is_more_specific_medicine
            )
        )

        if should_update:
            best_medicine = medicine
            best_score = score
            best_ocr_text = cleaned_text
            best_medicine_name = medicine_name

    if best_score < score_cutoff:
        return (
            None,
            best_score,
            best_ocr_text,
        )

    return (
        best_medicine,
        best_score,
        best_ocr_text,
    )
