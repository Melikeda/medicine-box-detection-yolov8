from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from src.ocr.ocr_pipeline import (
    OCRPipelineResult,
    get_candidate_texts,
    run_ocr_pipeline,
)
from src.ocr.ocr_reader import create_ocr_reader


MODEL_PATH = Path(
    "runs/detect/runs/detect/"
    "medicine_box_yolov8n-2/weights/best.pt"
)

IMAGE_PATH = Path(
    "data/samples/samples3.jpg"
)

OUTPUT_DIRECTORY = Path(
    "results/integration/yolo_ocr"
)

OCR_VARIANTS_DIRECTORY = (
    OUTPUT_DIRECTORY / "ocr_variants"
)

CONFIDENCE_THRESHOLD = 0.60
UPSCALE_FACTOR = 2.0
MINIMUM_OCR_CONFIDENCE = 0.0


def print_separator(
    title: str,
    separator_length: int = 60,
) -> None:
    """
    Terminalde başlık ve ayırıcı çizgi gösterir.
    """
    print(f"\n{title}")
    print("-" * separator_length)


def validate_paths() -> None:
    """
    Model ve görsel yollarının varlığını kontrol eder.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model bulunamadı: {MODEL_PATH}"
        )

    if not MODEL_PATH.is_file():
        raise ValueError(
            f"Model yolu bir dosya değil: {MODEL_PATH}"
        )

    if not IMAGE_PATH.exists():
        raise FileNotFoundError(
            f"Görsel bulunamadı: {IMAGE_PATH}"
        )

    if not IMAGE_PATH.is_file():
        raise ValueError(
            f"Görsel yolu bir dosya değil: {IMAGE_PATH}"
        )


def crop_best_detection(
    result: Results,
) -> tuple[np.ndarray, float] | None:
    """
    YOLO sonucundaki en yüksek güven skoruna sahip
    bounding box'ı seçer ve görüntüyü kırpar.

    Returns:
        (
            kırpılmış görüntü,
            YOLO güven skoru
        )

        Tespit bulunamazsa None döndürür.
    """
    if result.orig_img is None:
        return None

    if result.boxes is None:
        return None

    if len(result.boxes) == 0:
        return None

    original_image = result.orig_img

    image_height, image_width = (
        original_image.shape[:2]
    )

    confidence_values = (
        result.boxes.conf
        .detach()
        .cpu()
        .numpy()
    )

    best_box_index = int(
        confidence_values.argmax()
    )

    best_box = result.boxes[
        best_box_index
    ]

    coordinates = (
        best_box.xyxy[0]
        .detach()
        .cpu()
        .numpy()
    )

    x1, y1, x2, y2 = map(
        int,
        coordinates,
    )

    x1 = max(
        0,
        min(x1, image_width),
    )

    x2 = max(
        0,
        min(x2, image_width),
    )

    y1 = max(
        0,
        min(y1, image_height),
    )

    y2 = max(
        0,
        min(y2, image_height),
    )

    if x2 <= x1 or y2 <= y1:
        return None

    cropped_image = original_image[
        y1:y2,
        x1:x2,
    ]

    if cropped_image.size == 0:
        return None

    confidence = float(
        best_box.conf[0]
        .detach()
        .cpu()
        .item()
    )

    print_separator(
        "YOLO Tespit Bilgileri"
    )

    print(
        "Bounding box: "
        f"x1={x1}, y1={y1}, "
        f"x2={x2}, y2={y2}"
    )

    print(
        "YOLO güven skoru: "
        f"{confidence:.2f}"
    )

    print(
        "Crop boyutu: "
        f"{cropped_image.shape}"
    )

    return cropped_image, confidence


def save_image(
    image: np.ndarray,
    output_path: Path,
) -> Path:
    """
    Görüntüyü belirtilen dosya yoluna kaydeder.
    """
    if image.size == 0:
        raise ValueError(
            "Kaydedilecek görüntü boş olamaz."
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    success = cv2.imwrite(
        str(output_path),
        image,
    )

    if not success:
        raise IOError(
            f"Görüntü kaydedilemedi: {output_path}"
        )

    return output_path


def print_variant_results(
    pipeline_result: OCRPipelineResult,
) -> None:
    """
    Her preprocessing varyantının ham EasyOCR
    sonuçlarını terminalde gösterir.
    """
    print_separator(
        "Varyant Bazlı OCR Sonuçları"
    )

    for (
        variant_name,
        ocr_results,
    ) in pipeline_result.variant_results.items():
        print(f"\n[{variant_name}]")

        if not ocr_results:
            print("OCR sonucu bulunamadı.")
            continue

        for index, result in enumerate(
            ocr_results,
            start=1,
        ):
            if len(result) < 3:
                continue

            _, text, confidence = result

            print(
                f"{index}. {text} "
                f"(güven: "
                f"{float(confidence):.2f})"
            )


def print_candidates(
    pipeline_result: OCRPipelineResult,
) -> None:
    """
    Çoklu preprocessing sonucunda elde edilen
    temizlenmiş OCR adaylarını gösterir.
    """
    print_separator(
        "Birleştirilmiş OCR Adayları"
    )

    if not pipeline_result.candidates:
        print("OCR adayı oluşturulamadı.")
        return

    for index, candidate in enumerate(
        pipeline_result.candidates,
        start=1,
    ):
        candidate_type = (
            "birleşik"
            if candidate.is_combined
            else "doğrudan"
        )

        print(
            f"{index}. {candidate.text} "
            f"| güven: "
            f"{candidate.confidence:.2f} "
            f"| varyant: "
            f"{candidate.variant_name} "
            f"| tür: {candidate_type}"
        )


def print_saved_files(
    crop_output_path: Path,
    pipeline_result: OCRPipelineResult,
) -> None:
    """
    Pipeline sırasında kaydedilen dosyaları gösterir.
    """
    print_separator(
        "Kaydedilen Dosyalar"
    )

    print(
        f"YOLO crop: {crop_output_path}"
    )

    for (
        variant_name,
        variant_path,
    ) in pipeline_result.saved_variant_paths.items():
        print(
            f"{variant_name}: {variant_path}"
        )


def main() -> None:
    """
    YOLO crop ve çoklu OCR entegrasyonunu çalıştırır.

    İşlem sırası:
    1. Model ve görsel yollarını kontrol eder.
    2. YOLO ile ilaç kutusunu tespit eder.
    3. En yüksek güvenli bounding box'ı seçer.
    4. İlaç kutusunu kırpar.
    5. Crop görüntüsünü OCR pipeline'a gönderir.
    6. Dört preprocessing varyantı oluşturur.
    7. Her varyantta OCR çalıştırır.
    8. Komşu OCR parçalarını birleştirir.
    9. Oluşturulan adayları terminalde gösterir.
    """
    validate_paths()

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "\nYOLO Crop ve Çoklu OCR Entegrasyonu"
    )
    print("=" * 60)

    print(f"Model: {MODEL_PATH}")
    print(f"Görsel: {IMAGE_PATH}")

    print(
        "YOLO güven eşiği: "
        f"{CONFIDENCE_THRESHOLD}"
    )

    print(
        "OCR büyütme oranı: "
        f"{UPSCALE_FACTOR}"
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
            "\nYOLO tahmin sonucu alınamadı."
        )
        return

    crop_result = crop_best_detection(
        result=prediction_results[0],
    )

    if crop_result is None:
        print(
            "\nİlaç kutusu tespit edilemedi "
            "veya crop oluşturulamadı."
        )
        return

    cropped_image, _ = crop_result

    crop_output_path = (
        OUTPUT_DIRECTORY
        / "aferin_forte_yolo_crop.jpg"
    )

    save_image(
        image=cropped_image,
        output_path=crop_output_path,
    )

    print(
        f"\nCrop kaydedildi: "
        f"{crop_output_path}"
    )

    reader = create_ocr_reader(
        languages=["tr", "en"],
        use_gpu=False,
    )

    pipeline_result = run_ocr_pipeline(
        reader=reader,
        image_input=cropped_image,
        scale_factor=UPSCALE_FACTOR,
        minimum_confidence=(
            MINIMUM_OCR_CONFIDENCE
        ),
        save_preprocessed_images=True,
        output_directory=(
            OCR_VARIANTS_DIRECTORY
        ),
    )

    print_variant_results(
        pipeline_result=pipeline_result,
    )

    print_candidates(
        pipeline_result=pipeline_result,
    )

    candidate_texts = get_candidate_texts(
        pipeline_result=pipeline_result,
    )

    if not candidate_texts:
        print(
            "\nOCR tarafından kullanılabilir "
            "metin adayı oluşturulamadı."
        )
        return

    print_separator(
        "RapidFuzz İçin Hazır Metin Listesi"
    )

    for index, text in enumerate(
        candidate_texts,
        start=1,
    ):
        print(
            f"{index}. {text}"
        )

    print_saved_files(
        crop_output_path=crop_output_path,
        pipeline_result=pipeline_result,
    )

    print_separator(
        "Entegrasyon Tamamlandı"
    )

    print(
        "YOLO → Crop → Çoklu Preprocessing "
        "→ OCR → Candidate Fusion "
        "akışı başarıyla çalıştırıldı."
    )


if __name__ == "__main__":
    main()