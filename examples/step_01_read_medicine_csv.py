from pathlib import Path

from src.database.csv_reader import load_medicines


def main() -> None:
    csv_path = Path("data/database/medicines.csv")

    medicines = load_medicines(csv_path)

    print("\nİlaç Veritabanı")
    print("-" * 60)
    print(f"Toplam ilaç sayısı: {len(medicines)}")

    for index, medicine in enumerate(medicines, start=1):
        print(
            f"{index}. "
            f"{medicine['medicine_name']} | "
            f"{medicine['active_ingredient']} | "
            f"{medicine['dosage']} | "
            f"{medicine['form']} | "
            f"{medicine['manufacturer']}"
        )


if __name__ == "__main__":
    main()