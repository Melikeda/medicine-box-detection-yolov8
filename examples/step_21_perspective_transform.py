from pathlib import Path

import cv2
import numpy as np

from src.preprocessing.basic_operations import (
    display_image,
    read_image,
    save_image,
)
from src.preprocessing.geometric_operations import (
    resize_image,
)
from src.preprocessing.perspective_operations import (
    apply_perspective_transform,
    order_points,
)


def draw_selected_points(
    image,
    points,
):
    """
    Perspective Transform için seçilen dört köşeyi
    görüntü üzerinde işaretler.

    Args:
        image:
            İşaretleme yapılacak görüntü.

        points:
            Dört adet (x, y) koordinatı.

    Returns:
        Noktaları ve sınır çizgileri işaretlenmiş görüntü.
    """

    preview_image = image.copy()

    ordered_points = order_points(
        points
    ).astype(int)

    labels = [
        "Top Left",
        "Top Right",
        "Bottom Right",
        "Bottom Left",
    ]

    # Dört köşeyi ve etiketleri çiz.
    for index, point in enumerate(
        ordered_points
    ):
        x, y = point

        cv2.circle(
            preview_image,
            (x, y),
            radius=18,
            color=(0, 0, 255),
            thickness=-1,
        )

        cv2.putText(
            preview_image,
            labels[index],
            (x + 20, y - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 0, 255),
            thickness=3,
        )

    # Seçilen dört noktayı çizgilerle birleştir.
    cv2.polylines(
        preview_image,
        [
            ordered_points.reshape(
                (-1, 1, 2)
            )
        ],
        isClosed=True,
        color=(0, 255, 0),
        thickness=10,
    )

    return preview_image


def main() -> None:
    """
    Bir ilaç kutusunun dört köşesini kullanarak
    Perspective Transform uygular.
    """

    image_path = Path(
        "data/samples/medicine_sample.jpg"
    )

    output_path = Path(
        "results/preprocessing/"
        "medicine_sample_perspective_transform.jpg"
    )

    # Orijinal görüntüyü oku.
    image = read_image(
        image_path
    )

    print("\n===== PERSPECTIVE TRANSFORM INFORMATION =====")
    print(f"Orijinal Shape: {image.shape}")

    # İlaç kutusunun yaklaşık dört köşe koordinatı.
    #
    # Sıralama zorunlu değildir çünkü order_points()
    # bunları otomatik olarak düzenler.
    #
    # Bu değerler senin kullandığın örnek fotoğrafa göre
    # yaklaşık başlangıç değerleridir.
    source_points = np.array(
        [
            [700, 405],    # Sol üst
            [3050, 405],   # Sağ üst
            [3050, 1425],  # Sağ alt
            [700, 1425],   # Sol alt
        ],
        dtype=np.float32,
    )

    # Perspective Transform uygula.
    transformed_image = apply_perspective_transform(
        image=image,
        source_points=source_points,
    )

    print(
        f"Dönüştürülmüş Shape: "
        f"{transformed_image.shape}"
    )

    # Sonucu kaydet.
    save_image(
        transformed_image,
        output_path,
    )

    print(
        f"Perspective Transform görüntüsü kaydedildi: "
        f"{output_path}"
    )

    # Seçilen noktaları orijinal görüntü üzerinde göster.
    selected_points_image = draw_selected_points(
        image,
        source_points,
    )

    # Görüntüleri sadece ekran gösterimi için küçült.
    points_preview = resize_image(
        selected_points_image,
        width=800,
    )

    transformed_preview = resize_image(
        transformed_image,
        width=800,
    )

    print(
        "\nÖnce seçilen dört köşe noktası "
        "gösterilecektir."
    )

    display_image(
        points_preview,
        window_name="Selected Perspective Points",
    )

    print(
        "Şimdi Perspective Transform sonucu "
        "gösterilecektir."
    )

    display_image(
        transformed_preview,
        window_name="Perspective Transform Result",
    )


if __name__ == "__main__":
    main()