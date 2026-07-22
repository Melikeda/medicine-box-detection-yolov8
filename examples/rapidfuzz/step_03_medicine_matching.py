from pathlib import Path

from src.database.csv_reader import load_medicines
from src.matching.medicine_matcher import (
    DEFAULT_SCORE_CUTOFF,
    find_best_medicine_match,
)


def format_verified_value(
    value: str,
) -> str:
    """
    Henüz doğrulanmamış CSV değerlerini
    kullanıcı dostu biçimde gösterir.
    """
    if value == "VERIFY_FROM_OFFICIAL_LEAFLET":
        return "Bilgi henüz doğrulanmadı."

    return value


def print_medicine_result(
    ocr_text: str,
    medicine: dict[str, str],
    score: float,
    matched_medicine_name: str | None,
) -> None:
    """
    Eşleşen ilaç bilgilerini terminale
    düzenli şekilde yazdırır.
    """
    active_ingredient = format_verified_value(
        medicine["active_ingredient"]
    )

    dosage = format_verified_value(
        medicine["dosage"]
    )

    medicine_form = format_verified_value(
        medicine["form"]
    )

    print(f"OCR metni: {ocr_text}")
    print(
        "Karşılaştırılan ilaç adı: "
        f"{matched_medicine_name}"
    )
    print(
        "Eşleşen ilaç: "
        f"{medicine['medicine_name']}"
    )
    print(
        "Marka adı: "
        f"{medicine['brand_name']}"
    )
    print(f"Benzerlik skoru: {score:.2f}")
    print(f"Etken madde: {active_ingredient}")
    print(f"Doz: {dosage}")
    print(f"Form: {medicine_form}")
    print(f"Kategori: {medicine['category']}")


def main() -> None:
    csv_path = Path(
        "data/database/medicines.csv"
    )

    medicines = load_medicines(csv_path)

    test_texts = [
        "Paraol",
        "Dolorek",
        "Majezik",
        "Nurofcn Cold & Flu",
        "computer",
    ]

    print("\nİlaç Eşleştirme Sonuçları")
    print("=" * 60)
    print(
        "Minimum kabul skoru: "
        f"{DEFAULT_SCORE_CUTOFF:.0f}"
    )

    for ocr_text in test_texts:
        print("\n" + "-" * 60)

        (
            medicine,
            score,
            matched_medicine_name,
        ) = find_best_medicine_match(
            query_text=ocr_text,
            medicines=medicines,
        )

        if medicine is None:
            print(f"OCR metni: {ocr_text}")
            print(
                "En yüksek benzerlik skoru: "
                f"{score:.2f}"
            )
            print(
                "En yakın ilaç adı: "
                f"{matched_medicine_name}"
            )
            print(
                "Sonuç: Güvenilir eşleşme "
                "bulunamadı."
            )
            continue

        print_medicine_result(
            ocr_text=ocr_text,
            medicine=medicine,
            score=score,
            matched_medicine_name=(
                matched_medicine_name
            ),
        )


if __name__ == "__main__":
    main()