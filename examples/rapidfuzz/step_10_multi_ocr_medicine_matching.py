from pathlib import Path

from ultralytics import YOLO

from examples.rapidfuzz.step_07_yolo_crop_ocr import (
    CONFIDENCE_THRESHOLD,
    IMAGE_PATH,
    MODEL_PATH,
    crop_best_detection,
)
from src.database.csv_reader import load_medicines
from src.matching.medicine_matcher import (
    calculate_medicine_score,
    is_generic_single_word,
)
from src.ocr.ocr_pipeline import (
    get_candidate_texts,
    run_ocr_pipeline,
)
from src.ocr.ocr_reader import create_ocr_reader


MEDICINES_CSV_PATH = Path(
    "data/database/medicines.csv"
)

OUTPUT_DIRECTORY = Path(
    "results/integration/medicine_matching"
)

OCR_VARIANTS_DIRECTORY = (
    OUTPUT_DIRECTORY / "ocr_variants"
)

OCR_SCALE_FACTOR = 2.0
MINIMUM_OCR_CONFIDENCE = 0.0

MATCH_SCORE_CUTOFF = 80.0
TOP_MATCH_COUNT = 3


IGNORED_OCR_PHRASES = {
    "film kaplÄ± tablet",
    "film kapli tablet",
    "kaplÄ± tablet",
    "kapli tablet",
    "tablet",
    "parasetamol",
    "klorfeniramin maleat",
}


MEDICINE_NAME_SUFFIXES = {
    "fort",
    "forte",
    "plus",
    "extra",
    "cold",
    "flu",
}


def print_separator(
    title: str,
    separator_length: int = 60,
) -> None:
    """
    Terminalde baÅŸlÄ±k ve ayÄ±rÄ±cÄ± Ã§izgi gÃ¶sterir.
    """
    print(f"\n{title}")
    print("-" * separator_length)


def validate_paths() -> None:
    """
    Model, gÃ¶rsel ve CSV yollarÄ±nÄ± kontrol eder.
    """
    required_paths = {
        "YOLO modeli": MODEL_PATH,
        "Test gÃ¶rseli": IMAGE_PATH,
        "Ä°laÃ§ CSV dosyasÄ±": MEDICINES_CSV_PATH,
    }

    for path_name, path in required_paths.items():
        if not path.exists():
            raise FileNotFoundError(
                f"{path_name} bulunamadÄ±: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"{path_name} bir dosya deÄŸil: {path}"
            )


def normalize_filter_text(
    text: str,
) -> str:
    """
    OCR adayÄ±nÄ± filtreleme ve karÅŸÄ±laÅŸtÄ±rma iÃ§in
    standart biÃ§ime dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r.
    """
    return " ".join(
        text.strip().casefold().split()
    )


def contains_letter(
    text: str,
) -> bool:
    """
    Metnin en az bir alfabetik karakter iÃ§erip
    iÃ§ermediÄŸini kontrol eder.
    """
    return any(
        character.isalpha()
        for character in text
    )


def is_single_alphabetic_word(
    text: str,
) -> bool:
    """
    Metnin yalnÄ±zca harflerden oluÅŸan tek bir
    kelime olup olmadÄ±ÄŸÄ±nÄ± kontrol eder.
    """
    normalized_text = normalize_filter_text(
        text
    )

    return (
        " " not in normalized_text
        and normalized_text.isalpha()
    )


def is_valid_base_name_candidate(
    text: str,
) -> bool:
    """
    Bir OCR metninin ilaÃ§ adÄ±nÄ±n ana parÃ§asÄ± olarak
    kullanÄ±lmaya uygun olup olmadÄ±ÄŸÄ±nÄ± kontrol eder.

    Ã–rnek uygun adaylar:
        aferin
        ferin
        theraflu

    Ã–rnek uygun olmayan adaylar:
        forte
        tablet
        parasetamol
        650 mg
        fl kaph tablt
    """
    normalized_text = normalize_filter_text(
        text
    )

    if not normalized_text:
        return False

    if not is_single_alphabetic_word(
        normalized_text
    ):
        return False

    if not 3 <= len(normalized_text) <= 20:
        return False

    if normalized_text in MEDICINE_NAME_SUFFIXES:
        return False

    if normalized_text in IGNORED_OCR_PHRASES:
        return False

    if is_generic_single_word(
        normalized_text
    ):
        return False

    return True


def create_medicine_name_candidates(
    candidate_texts: list[str],
) -> list[str]:
    """
    FarklÄ± OCR varyantlarÄ±ndan elde edilen ilaÃ§ adÄ±
    parÃ§alarÄ±ndan yeni tam ad adaylarÄ± Ã¼retir.

    Ã–rnek:
        aferin + forte â†’ aferin forte

    Bu iÅŸlem OCR pipeline iÃ§indeki fiziksel komÅŸuluk
    birleÅŸtirmesinden farklÄ±dÄ±r. Burada tÃ¼m OCR
    varyantlarÄ±nÄ±n ortak aday havuzu kullanÄ±lÄ±r.

    Sadece:
    - Tek kelimelik ana isim adaylarÄ±
    - Bilinen ilaÃ§ adÄ± tamamlayÄ±cÄ±larÄ±

    birleÅŸtirilir. BÃ¶ylece:

        fl kaph tablt + forte

    gibi hatalÄ± birleÅŸimler engellenir.
    """
    normalized_candidates: list[str] = []
    seen_normalized_candidates: set[str] = set()

    for text in candidate_texts:
        normalized_text = normalize_filter_text(
            text
        )

        if not normalized_text:
            continue

        if normalized_text in seen_normalized_candidates:
            continue

        seen_normalized_candidates.add(
            normalized_text
        )

        normalized_candidates.append(
            normalized_text
        )

    suffix_candidates = [
        text
        for text in normalized_candidates
        if text in MEDICINE_NAME_SUFFIXES
    ]

    base_candidates = [
        text
        for text in normalized_candidates
        if is_valid_base_name_candidate(
            text
        )
    ]

    generated_candidates: list[str] = []
    seen_all_candidates: set[str] = set(
        normalized_candidates
    )

    for base_candidate in base_candidates:
        for suffix_candidate in suffix_candidates:
            combined_candidate = (
                f"{base_candidate} "
                f"{suffix_candidate}"
            )

            if combined_candidate in seen_all_candidates:
                continue

            seen_all_candidates.add(
                combined_candidate
            )

            generated_candidates.append(
                combined_candidate
            )

    return (
        normalized_candidates
        + generated_candidates
    )


def is_valid_matching_candidate(
    text: str,
) -> bool:
    """
    OCR adayÄ±nÄ±n ilaÃ§ adÄ± eÅŸleÅŸtirmesinde
    kullanÄ±lmaya uygun olup olmadÄ±ÄŸÄ±nÄ± kontrol eder.

    AÅŸaÄŸÄ±daki adaylar elenir:
    - BoÅŸ metinler
    - YalnÄ±zca sayÄ± ve noktalama iÃ§eren metinler
    - Doz bilgileri
    - Etken madde ve form bilgileri
    - Tek baÅŸÄ±na genel tamamlayÄ±cÄ± kelimeler
    """
    normalized_text = normalize_filter_text(
        text
    )

    if not normalized_text:
        return False

    if not contains_letter(
        normalized_text
    ):
        return False

    if normalized_text in IGNORED_OCR_PHRASES:
        return False

    if is_generic_single_word(
        normalized_text
    ):
        return False

    dosage_markers = {
        "mg",
        "ml",
        "mcg",
        "gr",
    }

    words = normalized_text.split()

    if any(
        marker in words
        for marker in dosage_markers
    ):
        return False

    digit_count = sum(
        character.isdigit()
        for character in normalized_text
    )

    letter_count = sum(
        character.isalpha()
        for character in normalized_text
    )

    if digit_count > letter_count:
        return False

    return True


def filter_candidate_texts(
    candidate_texts: list[str],
) -> list[str]:
    """
    RapidFuzz eÅŸleÅŸtirmesi Ã¶ncesinde OCR adaylarÄ±nÄ±
    temizler ve tekrarlarÄ± kaldÄ±rÄ±r.
    """
    filtered_texts: list[str] = []
    seen_texts: set[str] = set()

    for text in candidate_texts:
        normalized_text = normalize_filter_text(
            text
        )

        if not is_valid_matching_candidate(
            normalized_text
        ):
            continue

        if normalized_text in seen_texts:
            continue

        seen_texts.add(
            normalized_text
        )

        filtered_texts.append(
            normalized_text
        )

    return filtered_texts


def rank_medicine_matches(
    candidate_texts: list[str],
    medicines: list[dict[str, str]],
    top_count: int = 3,
) -> list[
    tuple[
        dict[str, str],
        float,
        str,
    ]
]:
    """
    Her OCR adayÄ±nÄ± her ilaÃ§ adÄ±yla karÅŸÄ±laÅŸtÄ±rÄ±r.

    Her ilaÃ§ iÃ§in yalnÄ±zca en yÃ¼ksek skorlu OCR
    adayÄ±nÄ± saklar ve sonuÃ§larÄ± skora gÃ¶re sÄ±ralar.

    Returns:
        [
            (
                ilaÃ§ kaydÄ±,
                eÅŸleÅŸme skoru,
                kullanÄ±lan OCR metni
            )
        ]
    """
    if top_count <= 0:
        raise ValueError(
            "top_count sÄ±fÄ±rdan bÃ¼yÃ¼k olmalÄ±dÄ±r."
        )

    best_matches_by_medicine: dict[
        str,
        tuple[
            dict[str, str],
            float,
            str,
        ],
    ] = {}

    for candidate_text in candidate_texts:
        for medicine in medicines:
            score, medicine_name = (
                calculate_medicine_score(
                    query_text=candidate_text,
                    medicine=medicine,
                )
            )

            if medicine_name is None:
                continue

            medicine_id = medicine.get(
                "medicine_id",
                medicine_name,
            )

            current_match = (
                best_matches_by_medicine.get(
                    medicine_id
                )
            )

            should_update = (
                current_match is None
                or score > current_match[1]
                or (
                    score == current_match[1]
                    and len(candidate_text)
                    > len(current_match[2])
                )
            )

            if should_update:
                best_matches_by_medicine[
                    medicine_id
                ] = (
                    medicine,
                    score,
                    candidate_text,
                )

    ranked_matches = sorted(
        best_matches_by_medicine.values(),
        key=lambda match: (
            match[1],
            len(match[2]),
            len(
                match[0].get(
                    "medicine_name",
                    "",
                )
            ),
        ),
        reverse=True,
    )

    return ranked_matches[
        :top_count
    ]


def print_ocr_candidates(
    candidate_texts: list[str],
) -> None:
    """
    OCR pipeline tarafÄ±ndan Ã¼retilen tÃ¼m metin
    adaylarÄ±nÄ± gÃ¶sterir.
    """
    print_separator(
        "TÃ¼m OCR AdaylarÄ±"
    )

    if not candidate_texts:
        print("OCR adayÄ± bulunamadÄ±.")
        return

    for index, text in enumerate(
        candidate_texts,
        start=1,
    ):
        print(
            f"{index}. {text}"
        )


def print_expanded_candidates(
    expanded_candidate_texts: list[str],
    original_candidate_texts: list[str],
) -> None:
    """
    OCR adaylarÄ±ndan sonradan Ã¼retilen tam ilaÃ§ adÄ±
    adaylarÄ±nÄ± gÃ¶sterir.
    """
    original_normalized_texts = {
        normalize_filter_text(text)
        for text in original_candidate_texts
    }

    generated_candidates = [
        text
        for text in expanded_candidate_texts
        if text not in original_normalized_texts
    ]

    print_separator(
        "Ãœretilen Tam Ä°laÃ§ AdÄ± AdaylarÄ±"
    )

    if not generated_candidates:
        print(
            "Yeni tam ilaÃ§ adÄ± adayÄ± Ã¼retilemedi."
        )
        return

    for index, text in enumerate(
        generated_candidates,
        start=1,
    ):
        print(
            f"{index}. {text}"
        )


def print_filtered_candidates(
    filtered_texts: list[str],
) -> None:
    """
    RapidFuzz'a gÃ¶nderilecek filtrelenmiÅŸ OCR
    adaylarÄ±nÄ± gÃ¶sterir.
    """
    print_separator(
        "RapidFuzz Ä°Ã§in FiltrelenmiÅŸ Adaylar"
    )

    if not filtered_texts:
        print(
            "EÅŸleÅŸtirmeye uygun OCR adayÄ± bulunamadÄ±."
        )
        return

    for index, text in enumerate(
        filtered_texts,
        start=1,
    ):
        print(
            f"{index}. {text}"
        )


def print_ranked_matches(
    ranked_matches: list[
        tuple[
            dict[str, str],
            float,
            str,
        ]
    ],
) -> None:
    """
    En iyi ilaÃ§ eÅŸleÅŸmelerini terminalde gÃ¶sterir.
    """
    print_separator(
        f"En Ä°yi {TOP_MATCH_COUNT} Ä°laÃ§ EÅŸleÅŸmesi"
    )

    if not ranked_matches:
        print("Ä°laÃ§ eÅŸleÅŸmesi bulunamadÄ±.")
        return

    for index, (
        medicine,
        score,
        ocr_text,
    ) in enumerate(
        ranked_matches,
        start=1,
    ):
        print(
            f"\n{index}. "
            f"{medicine.get('medicine_name', '-')}"
        )

        print(
            f"   EÅŸleÅŸme skoru: {score:.2f}"
        )

        print(
            f"   KullanÄ±lan OCR metni: {ocr_text}"
        )

        print(
            "   Marka: "
            f"{medicine.get('brand_name', '-')}"
        )

        print(
            "   Etken madde: "
            f"{medicine.get('active_ingredient', '-')}"
        )

        print(
            "   Doz: "
            f"{medicine.get('dosage', '-')}"
        )

        print(
            "   Form: "
            f"{medicine.get('form', '-')}"
        )

        print(
            "   Kategori: "
            f"{medicine.get('category', '-')}"
        )


def print_final_decision(
    ranked_matches: list[
        tuple[
            dict[str, str],
            float,
            str,
        ]
    ],
) -> None:
    """
    Skor eÅŸiÄŸine gÃ¶re nihai ilaÃ§ tahminini gÃ¶sterir.
    """
    print_separator(
        "Nihai Ä°laÃ§ Tahmini"
    )

    if not ranked_matches:
        print(
            "Tahmin Ã¼retilemedi."
        )
        return

    best_medicine, best_score, best_ocr_text = (
        ranked_matches[0]
    )

    if best_score < MATCH_SCORE_CUTOFF:
        print(
            "GÃ¼venilir bir ilaÃ§ eÅŸleÅŸmesi bulunamadÄ±."
        )

        print(
            f"En yÃ¼ksek skor: {best_score:.2f}"
        )

        print(
            "Gerekli minimum skor: "
            f"{MATCH_SCORE_CUTOFF:.2f}"
        )

        return

    print(
        "EÅŸleÅŸen ilaÃ§: "
        f"{best_medicine.get('medicine_name', '-')}"
    )

    print(
        f"EÅŸleÅŸme skoru: {best_score:.2f}"
    )

    print(
        f"En iyi OCR metni: {best_ocr_text}"
    )

    print(
        "Etken madde: "
        f"{best_medicine.get('active_ingredient', '-')}"
    )

    print(
        "Doz: "
        f"{best_medicine.get('dosage', '-')}"
    )

    print(
        "Form: "
        f"{best_medicine.get('form', '-')}"
    )


def main() -> None:
    """
    YOLO, Ã§oklu OCR ve RapidFuzz ilaÃ§ eÅŸleÅŸtirme
    entegrasyonunu Ã§alÄ±ÅŸtÄ±rÄ±r.

    Ä°ÅŸlem sÄ±rasÄ±:
    1. Model, gÃ¶rsel ve CSV dosyasÄ±nÄ± kontrol eder.
    2. Ä°laÃ§ veritabanÄ±nÄ± yÃ¼kler.
    3. YOLO ile ilaÃ§ kutusunu tespit eder.
    4. En gÃ¼venilir bounding box'Ä± kÄ±rpar.
    5. Ã‡oklu preprocessing ve OCR Ã§alÄ±ÅŸtÄ±rÄ±r.
    6. OCR adaylarÄ±ndan tam ilaÃ§ adÄ± adaylarÄ± Ã¼retir.
    7. AdaylarÄ± filtreler.
    8. RapidFuzz ile ilaÃ§ adlarÄ±nÄ± karÅŸÄ±laÅŸtÄ±rÄ±r.
    9. En iyi sonuÃ§larÄ± ve nihai tahmini gÃ¶sterir.
    """
    validate_paths()

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "\nYOLO, OCR ve RapidFuzz "
        "Ä°laÃ§ EÅŸleÅŸtirme Entegrasyonu"
    )
    print("=" * 60)

    medicines = load_medicines(
        csv_path=MEDICINES_CSV_PATH,
    )

    print(
        f"YÃ¼klenen ilaÃ§ sayÄ±sÄ±: "
        f"{len(medicines)}"
    )

    model = YOLO(
        str(MODEL_PATH)
    )

    prediction_results = model.predict(
        source=str(IMAGE_PATH),
        conf=CONFIDENCE_THRESHOLD,
        save=False,
        verbose=True,
    )

    if not prediction_results:
        print(
            "\nYOLO tahmin sonucu alÄ±namadÄ±."
        )
        return

    crop_result = crop_best_detection(
        result=prediction_results[0],
    )

    if crop_result is None:
        print(
            "\nÄ°laÃ§ kutusu tespit edilemedi "
            "veya crop oluÅŸturulamadÄ±."
        )
        return

    cropped_image, yolo_confidence = crop_result

    print(
        "\nOCR reader hazÄ±rlanÄ±yor..."
    )

    reader = create_ocr_reader(
        languages=["tr", "en"],
        use_gpu=False,
    )

    pipeline_result = run_ocr_pipeline(
        reader=reader,
        image_input=cropped_image,
        scale_factor=OCR_SCALE_FACTOR,
        minimum_confidence=(
            MINIMUM_OCR_CONFIDENCE
        ),
        save_preprocessed_images=True,
        output_directory=(
            OCR_VARIANTS_DIRECTORY
        ),
    )

    candidate_texts = get_candidate_texts(
        pipeline_result=pipeline_result,
    )

    print_ocr_candidates(
        candidate_texts=candidate_texts,
    )

    expanded_candidate_texts = (
        create_medicine_name_candidates(
            candidate_texts=candidate_texts,
        )
    )

    print_expanded_candidates(
        expanded_candidate_texts=(
            expanded_candidate_texts
        ),
        original_candidate_texts=candidate_texts,
    )

    filtered_candidate_texts = (
        filter_candidate_texts(
            candidate_texts=(
                expanded_candidate_texts
            ),
        )
    )

    print_filtered_candidates(
        filtered_texts=filtered_candidate_texts,
    )

    if not filtered_candidate_texts:
        print(
            "\nRapidFuzz eÅŸleÅŸtirmesi "
            "gerÃ§ekleÅŸtirilemedi."
        )
        return

    ranked_matches = rank_medicine_matches(
        candidate_texts=(
            filtered_candidate_texts
        ),
        medicines=medicines,
        top_count=TOP_MATCH_COUNT,
    )

    print_ranked_matches(
        ranked_matches=ranked_matches,
    )

    print_final_decision(
        ranked_matches=ranked_matches,
    )

    generated_candidate_count = (
        len(expanded_candidate_texts)
        - len(
            {
                normalize_filter_text(text)
                for text in candidate_texts
                if normalize_filter_text(text)
            }
        )
    )

    print_separator(
        "Pipeline Ã–zeti"
    )

    print(
        f"YOLO gÃ¼ven skoru: "
        f"{yolo_confidence:.2f}"
    )

    print(
        f"Toplam OCR adayÄ±: "
        f"{len(candidate_texts)}"
    )

    print(
        "Ãœretilen tam ad adayÄ±: "
        f"{generated_candidate_count}"
    )

    print(
        "FiltrelenmiÅŸ eÅŸleÅŸtirme adayÄ±: "
        f"{len(filtered_candidate_texts)}"
    )

    print(
        f"KarÅŸÄ±laÅŸtÄ±rÄ±lan ilaÃ§ sayÄ±sÄ±: "
        f"{len(medicines)}"
    )

    print_separator(
        "Entegrasyon TamamlandÄ±"
    )

    print(
        "YOLO â†’ Crop â†’ Ã‡oklu Preprocessing "
        "â†’ OCR â†’ Tam Ad AdayÄ± Ãœretme "
        "â†’ Aday Filtreleme â†’ RapidFuzz "
        "â†’ Ä°laÃ§ Tahmini akÄ±ÅŸÄ± tamamlandÄ±."
    )


if __name__ == "__main__":
    main()
