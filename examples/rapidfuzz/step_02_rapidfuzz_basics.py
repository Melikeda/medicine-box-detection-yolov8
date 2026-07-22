from rapidfuzz import fuzz


def main() -> None:
    medicine_name = "Parol"

    ocr_results = [
        "Parol",
        "Paraol",
        "Paro1",
        "PAROL",
        "Par",
        "Aspirin",
    ]

    print("\nRapidFuzz Karşılaştırmaları")
    print("-" * 50)

    for ocr_text in ocr_results:
        similarity_score = fuzz.ratio(
            ocr_text,
            medicine_name,
        )

        print(
            f"{ocr_text:<10} ↔ "
            f"{medicine_name:<10} | "
            f"Skor: {similarity_score:.2f}"
        )


if __name__ == "__main__":
    main()