from csv import DictReader
from pathlib import Path


REQUIRED_COLUMNS = {
    "medicine_id",
    "medicine_name",
    "brand_name",
    "active_ingredient",
    "dosage",
    "form",
    "category",
}


def load_medicines(
    csv_path: Path,
) -> list[dict[str, str]]:
    """
    CSV dosyasındaki ilaç kayıtlarını okur ve temizler.

    Beklenen CSV sütunları:
        - medicine_id
        - medicine_name
        - brand_name
        - active_ingredient
        - dosage
        - form
        - category

    Args:
        csv_path: medicines.csv dosyasının yolu.

    Returns:
        Her ilaç kaydını sözlük olarak içeren liste.

    Raises:
        FileNotFoundError:
            CSV dosyası bulunamazsa.

        ValueError:
            CSV dosyasında başlık satırı yoksa,
            gerekli sütunlardan biri eksikse
            veya geçerli ilaç kaydı bulunamazsa.
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV dosyası bulunamadı: {csv_path}"
        )

    if not csv_path.is_file():
        raise ValueError(
            f"Verilen yol bir dosya değil: {csv_path}"
        )

    medicines: list[dict[str, str]] = []

    with csv_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError(
                "CSV dosyasında başlık satırı bulunamadı."
            )

        fieldnames = {
            field_name.strip()
            for field_name in reader.fieldnames
            if field_name is not None
        }

        missing_columns = REQUIRED_COLUMNS - fieldnames

        if missing_columns:
            missing_columns_text = ", ".join(
                sorted(missing_columns)
            )

            raise ValueError(
                "CSV dosyasında gerekli sütunlar eksik: "
                f"{missing_columns_text}"
            )

        for row in reader:
            cleaned_row = {
                key.strip(): value.strip()
                for key, value in row.items()
                if key is not None and value is not None
            }

            medicine_name = cleaned_row.get(
                "medicine_name",
                "",
            )

            if medicine_name:
                medicines.append(cleaned_row)

    if not medicines:
        raise ValueError(
            "CSV dosyasında geçerli ilaç kaydı bulunamadı."
        )

    return medicines