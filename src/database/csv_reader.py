from csv import DictReader
from pathlib import Path

from src.barcode.normalize import is_plausible_barcode, normalize_barcode


REQUIRED_COLUMNS = {
    "medicine_id",
    "medicine_name",
    "brand_name",
    "active_ingredient",
    "dosage",
    "form",
    "category",
}

BARCODE_REQUIRED_COLUMNS = {
    "barcode",
    "medicine_id",
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


def load_medicine_barcodes(
    csv_path: Path,
) -> list[dict[str, str]]:
    """
    Barkod → medicine_id eşlemelerini okur.

    Beklenen sütunlar: barcode, medicine_id
    Dosya yoksa boş liste döner (barkod isteğe bağlı yan yoldur).
    """
    if not csv_path.exists():
        return []

    if not csv_path.is_file():
        raise ValueError(
            f"Verilen yol bir dosya değil: {csv_path}"
        )

    barcodes: list[dict[str, str]] = []
    seen: set[str] = set()

    with csv_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError(
                "Barkod CSV dosyasında başlık satırı bulunamadı."
            )

        fieldnames = {
            field_name.strip()
            for field_name in reader.fieldnames
            if field_name is not None
        }
        missing_columns = BARCODE_REQUIRED_COLUMNS - fieldnames
        if missing_columns:
            missing_text = ", ".join(sorted(missing_columns))
            raise ValueError(
                "Barkod CSV dosyasında gerekli sütunlar eksik: "
                f"{missing_text}"
            )

        for row in reader:
            raw_code = (row.get("barcode") or "").strip()
            medicine_id = (row.get("medicine_id") or "").strip()
            if not raw_code or not medicine_id:
                continue

            barcode = normalize_barcode(raw_code)
            if not is_plausible_barcode(barcode):
                continue
            if barcode in seen:
                continue

            seen.add(barcode)
            barcodes.append(
                {
                    "barcode": barcode,
                    "medicine_id": medicine_id,
                }
            )

    return barcodes