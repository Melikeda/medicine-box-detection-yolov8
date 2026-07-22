from pathlib import Path

import cv2
from ultralytics import YOLO
from ultralytics.engine.results import Results


MODEL_PATH = Path(
    "runs/detect/runs/detect/"
    "medicine_box_yolov8n-2/weights/best.pt"
)

SOURCE_PATH = Path(
    "data/samples/aferin_forte.jpg"
)

OUTPUT_PROJECT = Path(
    "runs/predict"
)

OUTPUT_NAME = "medicine_box_predictions"

CROP_OUTPUT_PATH = Path(
    "results/detection/crops"
)

CONFIDENCE_THRESHOLD = 0.60


def validate_paths() -> None:
    """
    Model ve kaynak yollarını kontrol eder.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model dosyası bulunamadı: {MODEL_PATH}"
        )

    if not SOURCE_PATH.exists():
        raise FileNotFoundError(
            f"Kaynak yol bulunamadı: {SOURCE_PATH}"
        )


def save_detection_crops(
    result: Results,
    image_index: int,
) -> list[Path]:
    """
    Bir YOLO tahmin sonucundaki bounding box'ları
    kullanarak ilaç kutularını kırpar ve kaydeder.

    Args:
        result:
            Tek bir görsele ait YOLO tahmin sonucu.

        image_index:
            İşlenen görselin sıra numarası.

    Returns:
        Kaydedilen crop görüntülerinin yolları.
    """
    original_image = result.orig_img

    if original_image is None:
        print(
            f"Görsel {image_index} için "
            "orijinal görüntü alınamadı."
        )
        return []

    if result.boxes is None:
        print(
            f"Görsel {image_index} için "
            "bounding box bulunamadı."
        )
        return []

    CROP_OUTPUT_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    saved_crop_paths: list[Path] = []

    image_height, image_width = (
        original_image.shape[:2]
    )

    source_path = Path(result.path)

    for box_index, box in enumerate(
        result.boxes,
        start=1,
    ):
        coordinates = box.xyxy[0].cpu().numpy()

        x1, y1, x2, y2 = map(
            int,
            coordinates,
        )

        x1 = max(0, min(x1, image_width))
        x2 = max(0, min(x2, image_width))
        y1 = max(0, min(y1, image_height))
        y2 = max(0, min(y2, image_height))

        if x2 <= x1 or y2 <= y1:
            print(
                f"Geçersiz bounding box atlandı: "
                f"{x1}, {y1}, {x2}, {y2}"
            )
            continue

        cropped_image = original_image[
            y1:y2,
            x1:x2,
        ]

        if cropped_image.size == 0:
            print(
                f"Görsel {image_index}, "
                f"kutu {box_index} boş olduğu için "
                "atlanıyor."
            )
            continue

        confidence = float(
            box.conf[0].cpu().item()
        )

        output_filename = (
            f"{source_path.stem}"
            f"_box_{box_index}"
            f"_conf_{confidence:.2f}.jpg"
        )

        output_path = (
            CROP_OUTPUT_PATH
            / output_filename
        )

        save_success = cv2.imwrite(
            str(output_path),
            cropped_image,
        )

        if not save_success:
            raise IOError(
                f"Crop görüntüsü kaydedilemedi: "
                f"{output_path}"
            )

        saved_crop_paths.append(
            output_path
        )

        print(
            f"Crop kaydedildi: {output_path}"
        )

        print(
            "Bounding box: "
            f"x1={x1}, y1={y1}, "
            f"x2={x2}, y2={y2}"
        )

        print(
            f"YOLO güven skoru: "
            f"{confidence:.2f}"
        )

    return saved_crop_paths


def run_prediction() -> None:
    """
    Eğitilmiş YOLOv8 modeliyle tahmin yapar
    ve tespit edilen ilaç kutularını kırpar.

    İşlem sırası:
    1. Model ve kaynak yollarını kontrol eder.
    2. YOLO modelini yükler.
    3. Kaynak görseller üzerinde tahmin yapar.
    4. Bounding box çizilmiş görselleri kaydeder.
    5. Tespit edilen ilaç kutularını kırpar.
    6. Crop görüntülerini ayrı klasöre kaydeder.
    """
    validate_paths()

    print(
        "\nYOLOv8 Prediction Started"
    )

    print("-" * 60)
    print(f"Model: {MODEL_PATH}")
    print(f"Source: {SOURCE_PATH}")

    print(
        f"Confidence: "
        f"{CONFIDENCE_THRESHOLD}"
    )

    model = YOLO(
        str(MODEL_PATH)
    )

    results = model.predict(
        source=str(SOURCE_PATH),
        conf=CONFIDENCE_THRESHOLD,
        save=True,
        project=str(OUTPUT_PROJECT),
        name=OUTPUT_NAME,
        exist_ok=True,
        verbose=True,
    )

    total_crop_count = 0

    for image_index, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"\nGörsel {image_index} işleniyor"
        )

        print("-" * 60)

        saved_crop_paths = (
            save_detection_crops(
                result=result,
                image_index=image_index,
            )
        )

        total_crop_count += len(
            saved_crop_paths
        )

    print(
        "\nYOLOv8 Prediction Completed"
    )

    print("-" * 60)

    print(
        "Tahmin çıktıları: "
        f"{OUTPUT_PROJECT / OUTPUT_NAME}"
    )

    print(
        f"Crop çıktıları: "
        f"{CROP_OUTPUT_PATH}"
    )

    print(
        f"İşlenen görsel sayısı: "
        f"{len(results)}"
    )

    print(
        f"Kaydedilen crop sayısı: "
        f"{total_crop_count}"
    )


if __name__ == "__main__":
    run_prediction()