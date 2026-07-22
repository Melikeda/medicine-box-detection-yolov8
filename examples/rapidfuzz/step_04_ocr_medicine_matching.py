from pathlib import Path

from src.database.csv_reader import load_medicines
from src.matching.medicine_matcher import (
    DEFAULT_SCORE_CUTOFF,
    find_best_match_from_texts,
)
from src.ocr.ocr_pipeline import run_ocr_pipeline
from src.ocr.ocr_reader import create_ocr_reader
from src.ocr.text_cleaner import (
    combine_texts,
    extract_texts,
)


UNVERIFIED_VALUE = "VERIFY_FROM_OFFICIAL_LEAFLET"


def print_separator(
    title: str,
    separator_length: int = 60,
) -> None:
    """
    Terminalde başlık ve ayırıcı çizgi gösterir.
    """
    print(f"\n{title}")
    print("-" * separator_length)


def print_text_list(
    title: str,
    texts: list[str],
) -> None:
    """
    Metin listesini terminalde numaralandırarak
    gösterir.
    """
    print_separator(title)

    if not texts:
        print("Gösterilecek metin bulunamadı.")
        return

    for index, text in enumerate(
        texts,
        start=1,
    ):
        print(f"{index}. {text}")


def remove_duplicate_texts(
    texts: list[str],
) -> list[str]:
    """
    Büyük-küçük harf farkını dikkate almadan
    tekrarlanan metinleri kaldırır.
    """
    unique_texts: list[str] = []
    seen_texts: set[str] = set()

    for text in texts:
        cleaned_text = text.strip()

        if not cleaned_text:
            continue

        normalized_text = cleaned_text.casefold()

        if normalized_text in seen_texts:
            continue

        unique_texts.append(cleaned_text)
        seen_texts.add(normalized_text)

    return unique_texts


def create_matching_texts(
    ocr_texts: list[str],
) -> list[str]:
    """
    RapidFuzz ile karşılaştırılacak OCR
    metinlerini oluşturur.

    Oluşturulan metinler:
    - Her OCR sonucu
    - İlk iki OCR sonucunun birleşimi
    - İlk üç OCR sonucunun birleşimi

    Ürün adı kutu üzerinde birkaç farklı satıra
    ayrılmış olabileceği için birleşik metinler
    de eşleştirmeye gönderilir.

    Örnek:
        NUROFCN
        COLD & FLU

    Birleşik metin:
        NUROFCN COLD & FLU
    """
    cleaned_ocr_texts = [
        text.strip()
        for text in ocr_texts
        if text.strip()
    ]

    matching_texts = list(
        cleaned_ocr_texts
    )

    if len(cleaned_ocr_texts) >= 2:
        first_two_texts = " ".join(
            cleaned_ocr_texts[:2]
        )

        matching_texts.append(
            first_two_texts
        )

    if len(cleaned_ocr_texts) >= 3:
        first_three_texts = " ".join(
            cleaned_ocr_texts[:3]
        )

        matching_texts.append(
            first_three_texts
        )

    return remove_duplicate_texts(
        matching_texts
    )


def format_medicine_value(
    value: str | None,
) -> str:
    """
    CSV'deki boş veya henüz doğrulanmamış
    değerleri kullanıcı dostu metne dönüştürür.
    """
    if value is None:
        return "Bilgi henüz doğrulanmadı."

    cleaned_value = value.strip()

    if not cleaned_value:
        return "Bilgi henüz doğrulanmadı."

    if cleaned_value == UNVERIFIED_VALUE:
        return "Bilgi henüz doğrulanmadı."

    return cleaned_value


def print_medicine_information(
    medicine: dict[str, str],
    score: float,
    matched_text: str | None,
) -> None:
    """
    Eşleşen ilacın bilgilerini terminalde
    düzenli şekilde gösterir.
    """
    print_separator(
        "En İyi Eşleşmeyi Sağlayan OCR Metni"
    )

    if matched_text is None:
        print("Eşleşme metni bulunamadı.")
    else:
        print(matched_text)

    medicine_id = format_medicine_value(
        medicine.get("medicine_id")
    )

    medicine_name = format_medicine_value(
        medicine.get("medicine_name")
    )

    brand_name = format_medicine_value(
        medicine.get("brand_name")
    )

    print_separator(
        "Eşleşme Sonucu"
    )

    print(f"İlaç ID: {medicine_id}")
    print(f"İlaç adı: {medicine_name}")
    print(f"Marka adı: {brand_name}")
    print(f"Eşleşme skoru: {score:.2f}")

    active_ingredient = format_medicine_value(
        medicine.get("active_ingredient")
    )

    dosage = format_medicine_value(
        medicine.get("dosage")
    )

    medicine_form = format_medicine_value(
        medicine.get("form")
    )

    category = format_medicine_value(
        medicine.get("category")
    )

    print_separator(
        "İlaç Bilgileri"
    )

    print(
        f"Etken madde: {active_ingredient}"
    )
    print(f"Doz: {dosage}")
    print(f"Form: {medicine_form}")
    print(f"Kategori: {category}")


def main() -> None:
    """
    OCR, RapidFuzz ve CSV veritabanı
    entegrasyonunu çalıştırır.

    İşlem sırası:
    1. CSV ilaç kayıtlarını yükler.
    2. Görsel üzerinde OCR çalıştırır.
    3. OCR metinlerini çıkarır.
    4. Ürün adı için birleşik metinler oluşturur.
    5. Metinleri medicine_name alanlarıyla
       karşılaştırır.
    6. En iyi ilaç eşleşmesini gösterir.
    """
    image_path = Path(
        "data/samples/aferin_forte.jpg"
    )

    csv_path = Path(
        "data/database/medicines.csv"
    )

    print(
        "\nOCR ve İlaç Eşleştirme Entegrasyonu"
    )
    print("=" * 60)

    print(f"Görsel: {image_path}")
    print(f"CSV: {csv_path}")

    print(
        "Minimum eşleşme skoru: "
        f"{DEFAULT_SCORE_CUTOFF:.0f}"
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Görsel bulunamadı: {image_path}"
        )

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV dosyası bulunamadı: {csv_path}"
        )

    medicines = load_medicines(
        csv_path
    )

    reader = create_ocr_reader(
        languages=["tr", "en"],
        use_gpu=False,
    )

    ocr_results = run_ocr_pipeline(
        reader=reader,
        image_input=image_path,
    )

    ocr_texts = extract_texts(
        ocr_results
    )

    if not ocr_texts:
        print(
            "\nOCR tarafından herhangi bir "
            "metin okunamadı."
        )
        return

    print_text_list(
        title=(
            "OCR Tarafından Okunan Metinler"
        ),
        texts=ocr_texts,
    )

    combined_text = combine_texts(
        ocr_texts
    )

    print_separator(
        "Birleştirilmiş OCR Metni"
    )
    print(combined_text)

    matching_texts = create_matching_texts(
        ocr_texts
    )

    print_text_list(
        title=(
            "RapidFuzz ile "
            "Karşılaştırılacak Metinler"
        ),
        texts=matching_texts,
    )

    (
        matched_medicine,
        score,
        matched_text,
    ) = find_best_match_from_texts(
        texts=matching_texts,
        medicines=medicines,
        score_cutoff=DEFAULT_SCORE_CUTOFF,
    )

    if matched_medicine is None:
        print_separator(
            "Eşleşme Sonucu"
        )

        print(
            "Minimum eşleşme skorunu geçen "
            "bir ilaç adı bulunamadı."
        )

        print(
            "En yüksek eşleşme skoru: "
            f"{score:.2f}"
        )

        if matched_text is not None:
            print(
                "En yüksek skoru sağlayan "
                f"OCR metni: {matched_text}"
            )

        return

    print_medicine_information(
        medicine=matched_medicine,
        score=score,
        matched_text=matched_text,
    )


if __name__ == "__main__":
    main()