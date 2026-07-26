from pathlib import Path

from src.services.candidate_processor import normalize_filter_text
from src.services.config import PipelineConfig
from src.services.medicine_analyzer import (
    MedicineAnalysisResult,
    analyze_medicine_box,
)


IMAGE_PATH = Path("data/samples/samples3.jpg")

CONFIG = PipelineConfig()


def print_separator(
    title: str,
    separator_length: int = 60,
) -> None:
    """Terminalde başlık ve ayırıcı çizgi gösterir."""
    print(f"\n{title}")
    print("-" * separator_length)


def validate_paths() -> None:
    """Model, görsel ve CSV yollarını kontrol eder."""
    required_paths = {
        "YOLO modeli": CONFIG.model_path,
        "Test görseli": IMAGE_PATH,
        "İlaç CSV dosyası": CONFIG.medicines_csv_path,
    }

    for path_name, path in required_paths.items():
        if not path.exists():
            raise FileNotFoundError(
                f"{path_name} bulunamadı: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"{path_name} bir dosya değil: {path}"
            )


def print_ocr_candidates(
    candidate_texts: list[str],
) -> None:
    """OCR pipeline tarafından üretilen tüm metin adaylarını gösterir."""
    print_separator("Tüm OCR Adayları")

    if not candidate_texts:
        print("OCR adayı bulunamadı.")
        return

    for index, text in enumerate(candidate_texts, start=1):
        print(f"{index}. {text}")


def print_expanded_candidates(
    expanded_candidate_texts: list[str],
    original_candidate_texts: list[str],
) -> None:
    """OCR adaylarından sonradan üretilen tam ilaç adı adaylarını gösterir."""
    original_normalized_texts = {
        normalize_filter_text(text)
        for text in original_candidate_texts
    }

    generated_candidates = [
        text
        for text in expanded_candidate_texts
        if text not in original_normalized_texts
    ]

    print_separator("Üretilen Tam İlaç Adı Adayları")

    if not generated_candidates:
        print("Yeni tam ilaç adı adayı üretilemedi.")
        return

    for index, text in enumerate(generated_candidates, start=1):
        print(f"{index}. {text}")


def print_filtered_candidates(
    filtered_texts: list[str],
) -> None:
    """RapidFuzz'a gönderilecek filtrelenmiş OCR adaylarını gösterir."""
    print_separator("RapidFuzz İçin Filtrelenmiş Adaylar")

    if not filtered_texts:
        print("Eşleştirmeye uygun OCR adayı bulunamadı.")
        return

    for index, text in enumerate(filtered_texts, start=1):
        print(f"{index}. {text}")


def print_ranked_matches(
    result: MedicineAnalysisResult,
) -> None:
    """En iyi ilaç eşleşmelerini terminalde gösterir."""
    print_separator(
        f"En İyi {CONFIG.top_match_count} İlaç Eşleşmesi"
    )

    if not result.ranked_matches:
        print("İlaç eşleşmesi bulunamadı.")
        return

    for index, (medicine, score, ocr_text) in enumerate(
        result.ranked_matches,
        start=1,
    ):
        print(f"\n{index}. {medicine.get('medicine_name', '-')}")
        print(f"   Eşleşme skoru: {score:.2f}")
        print(f"   Kullanılan OCR metni: {ocr_text}")
        print(f"   Marka: {medicine.get('brand_name', '-')}")
        print(
            "   Etken madde: "
            f"{medicine.get('active_ingredient', '-')}"
        )
        print(f"   Doz: {medicine.get('dosage', '-')}")
        print(f"   Form: {medicine.get('form', '-')}")
        print(f"   Kategori: {medicine.get('category', '-')}")


def print_final_decision(
    result: MedicineAnalysisResult,
) -> None:
    """Skor eşiğine göre nihai ilaç tahminini gösterir."""
    print_separator("Nihai İlaç Tahmini")

    if not result.ranked_matches:
        print("Tahmin üretilemedi.")
        return

    if not result.success:
        print(result.error or "Güvenilir bir ilaç eşleşmesi bulunamadı.")
        print(f"En yüksek skor: {result.match_score:.2f}")
        print(
            f"Gerekli minimum skor: {CONFIG.match_score_cutoff:.2f}"
        )
        return

    medicine = result.medicine or {}

    print(f"Eşleşen ilaç: {medicine.get('medicine_name', '-')}")
    print(f"Eşleşme skoru: {result.match_score:.2f}")
    print(f"En iyi OCR metni: {result.best_ocr_text}")
    print(
        "Etken madde: "
        f"{medicine.get('active_ingredient', '-')}"
    )
    print(f"Doz: {medicine.get('dosage', '-')}")
    print(f"Form: {medicine.get('form', '-')}")


def print_pipeline_summary(
    result: MedicineAnalysisResult,
) -> None:
    """Pipeline özet istatistiklerini gösterir."""
    generated_candidate_count = len(result.expanded_candidates) - len(
        {
            normalize_filter_text(text)
            for text in result.ocr_candidates
            if normalize_filter_text(text)
        }
    )

    print_separator("Pipeline Özeti")

    if result.yolo_confidence is not None:
        print(f"YOLO güven skoru: {result.yolo_confidence:.2f}")

    print(f"Toplam OCR adayı: {len(result.ocr_candidates)}")
    print(f"Üretilen tam ad adayı: {generated_candidate_count}")
    print(
        "Filtrelenmiş eşleştirme adayı: "
        f"{len(result.filtered_candidates)}"
    )
    print(
        f"Karşılaştırılan ilaç sayısı: {result.medicines_compared}"
    )


def main() -> None:
    """
    analyze_medicine_box() servisini çalıştırır ve sonuçları gösterir.

    İş mantığı src/services/medicine_analyzer.py içindedir.
    Bu script yalnızca demo ve terminal çıktısı sağlar.
    """
    validate_paths()

    CONFIG.output_directory.mkdir(parents=True, exist_ok=True)

    print("\nYOLO, OCR ve RapidFuzz İlaç Eşleştirme Entegrasyonu")
    print("=" * 60)

    result = analyze_medicine_box(
        image_path=IMAGE_PATH,
        config=CONFIG,
        save_debug_outputs=True,
    )

    print_ocr_candidates(result.ocr_candidates)
    print_expanded_candidates(
        expanded_candidate_texts=result.expanded_candidates,
        original_candidate_texts=result.ocr_candidates,
    )
    print_filtered_candidates(result.filtered_candidates)

    if not result.filtered_candidates:
        print(f"\n{result.error or 'Eşleştirme gerçekleştirilemedi.'}")
        return

    print_ranked_matches(result)
    print_final_decision(result)
    print_pipeline_summary(result)

    print_separator("Entegrasyon Tamamlandı")

    if result.success:
        print(
            "YOLO → Crop → Çoklu Preprocessing → OCR → "
            "Tam Ad Adayı Üretme → Aday Filtreleme → "
            "RapidFuzz → İlaç Tahmini akışı tamamlandı."
        )
    else:
        print(result.error or "Pipeline tamamlandı ancak eşleşme bulunamadı.")


if __name__ == "__main__":
    main()
