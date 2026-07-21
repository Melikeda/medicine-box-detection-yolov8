from rapidfuzz import fuzz


DEFAULT_SCORE_CUTOFF = 80.0


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


def normalize_text(
    text: str,
) -> str:
    """
    Karşılaştırma için metni temizler.

    Büyük-küçük harf farkını ortadan kaldırır
    ve baştaki/sondaki boşlukları temizler.
    """
    return text.strip().casefold()


def is_generic_single_word(
    text: str,
) -> bool:
    """
    OCR metninin tek başına ilaç seçtirmemesi
    gereken genel bir kelime olup olmadığını
    kontrol eder.

    Örnek:
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


def get_medicine_name(
    medicine: dict[str, str],
) -> str | None:
    """
    İlaç kaydındaki medicine_name değerini
    temizleyerek döndürür.

    medicine_name boşsa None döndürür.
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
    OCR metni ile ilacın tam adı arasındaki
    benzerlik skorunu hesaplar.

    Skor 0 ile 100 arasındadır.
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
    Tek bir OCR metnini ilacın medicine_name
    alanıyla karşılaştırır.

    Returns:
        (
            eşleşme skoru,
            karşılaştırılan ilaç adı
        )
    """
    medicine_name = get_medicine_name(
        medicine
    )

    if medicine_name is None:
        return 0.0, None

    score = calculate_text_similarity(
        query_text=query_text,
        medicine_name=medicine_name,
    )

    return score, medicine_name


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
    Tek bir OCR metni için veritabanındaki
    en iyi ilaç eşleşmesini bulur.

    Eşleştirmede yalnızca medicine_name
    alanı kullanılır.

    Genel kelimeler tek başına ilaç seçtiremez.

    Returns:
        (
            eşleşen ilaç kaydı,
            eşleşme skoru,
            eşleşen medicine_name
        )
    """
    cleaned_query = query_text.strip()

    if not cleaned_query:
        return None, 0.0, None

    if is_generic_single_word(cleaned_query):
        return None, 0.0, None

    best_medicine: dict[str, str] | None = None
    best_score = 0.0
    best_medicine_name: str | None = None

    for medicine in medicines:
        score, medicine_name = (
            calculate_medicine_score(
                query_text=cleaned_query,
                medicine=medicine,
            )
        )

        if medicine_name is None:
            continue

        is_higher_score = score > best_score

        is_same_score = score == best_score

        is_more_specific_name = (
            best_medicine_name is None
            or len(medicine_name)
            > len(best_medicine_name)
        )

        if is_higher_score or (
            is_same_score
            and is_more_specific_name
        ):
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
    Birden fazla OCR metni arasından en iyi
    ilaç eşleşmesini bulur.

    Genel kelimeler tek başına değerlendirilmez.

    Skorlar eşitse daha uzun OCR metni ve daha
    spesifik ilaç adı tercih edilir.

    Returns:
        (
            eşleşen ilaç kaydı,
            eşleşme skoru,
            en iyi OCR metni
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