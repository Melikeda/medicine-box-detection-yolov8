from pathlib import Path

from src.ocr.ocr_pipeline import run_ocr_pipeline
from src.ocr.ocr_reader import create_ocr_reader
from src.ocr.text_cleaner import (
    combine_texts,
    extract_texts,
)


def print_text_list(
    title: str,
    texts: list[str],
) -> None:
    """
    Metin listesini terminale düzenli şekilde yazdırır.
    """
    print(f"\n{title}")
    print("-" * 60)

    if not texts:
        print("Gösterilecek metin bulunamadı.")
        return

    for index, text in enumerate(texts, start=1):
        print(f"{index}. {text}")


def main() -> None:
    input_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    reader = create_ocr_reader(
        languages=["tr", "en"],
        use_gpu=False,
    )

    print("OCR pipeline çalıştırılıyor...")

    ocr_results = run_ocr_pipeline(
        reader=reader,
        image_path=input_path,
    )

    all_texts = extract_texts(
        ocr_results=ocr_results,
        minimum_confidence=0.0,
    )

    reliable_texts = extract_texts(
        ocr_results=ocr_results,
        minimum_confidence=0.70,
    )

    combined_text = combine_texts(
        texts=reliable_texts,
        separator=" | ",
    )

    print_text_list(
        title="TÜM OCR METİNLERİ",
        texts=all_texts,
    )

    print_text_list(
        title="GÜVEN SKORU 0.70 VE ÜZERİ OLAN METİNLER",
        texts=reliable_texts,
    )

    print("\nBİRLEŞTİRİLMİŞ METİN")
    print("-" * 60)

    if combined_text:
        print(combined_text)
    else:
        print("Birleştirilecek metin bulunamadı.")


if __name__ == "__main__":
    main()