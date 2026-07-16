from src.preprocessing.color_operations import (
    apply_clahe,
    convert_to_grayscale,
)  #Sadece daha önce yazdığımız fonksiyonları içeri aktarıyor.
from src.preprocessing.filter_operations import (
    apply_median_blur,
)
from src.preprocessing.geometric_operations import (
    crop_image,
    resize_image,
)
from src.preprocessing.morphological_operations import (
    apply_closing,
    apply_opening,
)
from src.preprocessing.threshold_operations import (
    apply_adaptive_threshold,
)


def preprocess_for_ocr(                #Bu fonksiyonun amacı yalnızca bir tane OCR okuyabilsin diye resmi hazırla.
    image,
    resize_width: int | None = None,
    crop_region: tuple[int, int, int, int] | None = None,
    median_kernel_size: int = 5,
    clahe_clip_limit: float = 2.0,
    clahe_tile_grid_size: tuple[int, int] = (8, 8),
    adaptive_block_size: int = 11,
    adaptive_constant: int = 2,
    morphology_kernel_size: tuple[int, int] = (3, 3),
):
    """
    Görüntüyü OCR için ön işler.

    İşlem sırası:
        1. İsteğe bağlı resize
        2. İsteğe bağlı crop
        3. Grayscale
        4. Median Blur
        5. CLAHE
        6. Adaptive Threshold
        7. Opening
        8. Closing

    Args:
        image:
            OpenCV tarafından okunmuş görüntü.

        resize_width:
            Görüntünün oranı korunarak getirileceği genişlik.
            None verilirse resize uygulanmaz.

        crop_region:
            Crop alanı: (x, y, width, height).
            None verilirse crop uygulanmaz.

        median_kernel_size:
            Median Blur kernel boyutu.

        clahe_clip_limit:
            CLAHE kontrast sınırı.

        clahe_tile_grid_size:
            CLAHE bölgesel ızgara boyutu.

        adaptive_block_size:
            Adaptive Threshold komşuluk boyutu.

        adaptive_constant:
            Yerel eşik değerinden çıkarılacak sabit.

        morphology_kernel_size:
            Opening ve Closing kernel boyutu.

    Returns:
        OCR için hazırlanmış binary görüntü.

    Raises:
        ValueError:
            Görüntü boş veya geçersizse.
    """

    if image is None:       #ilk kontrol: Programun çökmesini engelliyoruz.
        raise ValueError(
            "Pipeline için geçerli bir görüntü gereklidir."
        )

    processed_image = image.copy()

    # Görüntü çok büyükse oranı korunarak küçült.
    if resize_width is not None:
        processed_image = resize_image(
            processed_image,
            width=resize_width,
        )

    # Belirli bir bölge verildiyse görüntüyü kırp.
    if crop_region is not None:
        x, y, width, height = crop_region

        processed_image = crop_image(
            image=processed_image,
            x=x,
            y=y,
            width=width,
            height=height,
        )

    # Renk bilgisini kaldır ve tek kanallı görüntü oluştur.
    grayscale_image = convert_to_grayscale(
        processed_image
    )

    # Küçük gürültüleri azalt.
    blurred_image = apply_median_blur(
        grayscale_image,
        kernel_size=median_kernel_size,
    )

    # Yerel kontrastı artır.
    clahe_image = apply_clahe(
        blurred_image,
        clip_limit=clahe_clip_limit,
        tile_grid_size=clahe_tile_grid_size,
    )

    # Görüntüyü binary hale getir.
    threshold_image = apply_adaptive_threshold(
        grayscale_image=clahe_image,
        max_value=255,
        block_size=adaptive_block_size,
        constant=adaptive_constant,
    )

    # Küçük beyaz gürültüleri azalt.
    opened_image = apply_opening(
        threshold_image,
        kernel_size=morphology_kernel_size,
        iterations=1,
    )

    # Küçük siyah boşlukları kapat.
    final_image = apply_closing(
        opened_image,
        kernel_size=morphology_kernel_size,
        iterations=1,
    )

    return final_image