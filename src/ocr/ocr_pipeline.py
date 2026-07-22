from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import easyocr
import numpy as np


ImageInput = str | Path | np.ndarray

DEFAULT_BLUR_THRESHOLD = 80.0
BLURRY_IMAGE_SCALE_FACTOR = 3.0


@dataclass
class OCRCandidate:
    """
    OCR sonucundan üretilen tek bir metin adayını temsil eder.
    """

    text: str
    confidence: float
    variant_name: str
    is_combined: bool = False


@dataclass
class OCRPipelineResult:
    """
    Çoklu OCR pipeline sonucunu temsil eder.
    """

    candidates: list[OCRCandidate]
    variant_results: dict[str, list[Any]]
    saved_variant_paths: dict[str, Path]


def load_ocr_image(
    image_input: ImageInput,
) -> np.ndarray:
    """
    OCR için görüntüyü yükler.

    Desteklenen girişler:
    - str dosya yolu
    - Path dosya yolu
    - OpenCV numpy.ndarray görüntüsü
    """
    if isinstance(
        image_input,
        np.ndarray,
    ):
        if image_input.size == 0:
            raise ValueError(
                "OCR'a verilen görüntü boş."
            )

        return image_input.copy()

    image_path = Path(
        image_input
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Görüntü bulunamadı: {image_path}"
        )

    if not image_path.is_file():
        raise ValueError(
            f"Verilen yol bir dosya değil: {image_path}"
        )

    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise ValueError(
            "Görüntü OpenCV ile okunamadı: "
            f"{image_path}"
        )

    return image


def upscale_image(
    image: np.ndarray,
    scale_factor: float = 2.0,
) -> np.ndarray:
    """
    Görüntüyü OCR öncesinde INTER_CUBIC ile büyütür.
    """
    if image.size == 0:
        raise ValueError(
            "Büyütülecek görüntü boş."
        )

    if scale_factor <= 0:
        raise ValueError(
            "scale_factor sıfırdan büyük olmalıdır."
        )

    return cv2.resize(
        image,
        None,
        fx=scale_factor,
        fy=scale_factor,
        interpolation=cv2.INTER_CUBIC,
    )


def convert_to_grayscale(
    image: np.ndarray,
) -> np.ndarray:
    """
    Görüntüyü gri tonlamaya dönüştürür.
    """
    if image.ndim == 2:
        return image.copy()

    if image.ndim == 3:
        return cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

    raise ValueError(
        "Görüntü 2 veya 3 boyutlu olmalıdır. "
        f"Alınan boyut: {image.ndim}"
    )


def calculate_blur_score(
    image: np.ndarray,
) -> float:
    """
    Laplacian varyansı ile görüntünün netlik skorunu hesaplar.

    Genel yorum:
    - Yüksek skor: daha net görüntü
    - Düşük skor: daha bulanık görüntü

    Eşik görüntü boyutuna ve kameraya göre değişebilir.
    """
    if image.size == 0:
        raise ValueError(
            "Bulanıklığı ölçülecek görüntü boş."
        )

    grayscale_image = convert_to_grayscale(
        image
    )

    return float(
        cv2.Laplacian(
            grayscale_image,
            cv2.CV_64F,
        ).var()
    )


def apply_sharpening(
    image: np.ndarray,
) -> np.ndarray:
    """
    Görüntüdeki yazı kenarlarını belirginleştirir.
    """
    sharpening_kernel = np.array(
        [
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0],
        ],
        dtype=np.float32,
    )

    return cv2.filter2D(
        image,
        ddepth=-1,
        kernel=sharpening_kernel,
    )


def apply_unsharp_mask(
    image: np.ndarray,
) -> np.ndarray:
    """
    Normal unsharp mask uygular.
    """
    blurred_image = cv2.GaussianBlur(
        image,
        (0, 0),
        sigmaX=2.0,
    )

    return cv2.addWeighted(
        image,
        1.8,
        blurred_image,
        -0.8,
        0,
    )


def apply_strong_unsharp_mask(
    image: np.ndarray,
) -> np.ndarray:
    """
    Bulanık yazılar için daha güçlü unsharp mask uygular.

    Çok ağır hareket bulanıklığını geri getiremez;
    yalnızca korunmuş kenar bilgisini güçlendirir.
    """
    blurred_image = cv2.GaussianBlur(
        image,
        (0, 0),
        sigmaX=3.0,
    )

    return cv2.addWeighted(
        image,
        2.4,
        blurred_image,
        -1.4,
        0,
    )


def apply_clahe(
    image: np.ndarray,
    clip_limit: float = 2.5,
    tile_grid_size: tuple[int, int] = (
        8,
        8,
    ),
) -> np.ndarray:
    """
    Düşük ışıklı ve düşük kontrastlı görüntülerde
    yerel kontrastı artırır.
    """
    if clip_limit <= 0:
        raise ValueError(
            "clip_limit sıfırdan büyük olmalıdır."
        )

    grayscale_image = convert_to_grayscale(
        image
    )

    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=tile_grid_size,
    )

    return clahe.apply(
        grayscale_image
    )


def apply_bilateral_filter(
    image: np.ndarray,
) -> np.ndarray:
    """
    Gürültüyü azaltırken kenarları korumaya çalışır.
    """
    return cv2.bilateralFilter(
        image,
        d=7,
        sigmaColor=55,
        sigmaSpace=55,
    )


def apply_bilateral_clahe(
    image: np.ndarray,
) -> np.ndarray:
    """
    Önce gürültüyü azaltır, sonra yerel kontrastı artırır.
    """
    grayscale_image = convert_to_grayscale(
        image
    )

    filtered_image = apply_bilateral_filter(
        grayscale_image
    )

    return apply_clahe(
        filtered_image
    )


def apply_adaptive_threshold(
    image: np.ndarray,
) -> np.ndarray:
    """
    Görüntünün farklı bölgelerindeki değişken ışığa göre
    adaptif eşikleme uygular.
    """
    grayscale_image = convert_to_grayscale(
        image
    )

    denoised_image = cv2.GaussianBlur(
        grayscale_image,
        (3, 3),
        0,
    )

    return cv2.adaptiveThreshold(
        denoised_image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        9,
    )


def apply_otsu_threshold(
    image: np.ndarray,
) -> np.ndarray:
    """
    Otsu yöntemiyle binary görüntü oluşturur.
    """
    grayscale_image = convert_to_grayscale(
        image
    )

    blurred_image = cv2.GaussianBlur(
        grayscale_image,
        (3, 3),
        0,
    )

    _, threshold_image = cv2.threshold(
        blurred_image,
        0,
        255,
        cv2.THRESH_BINARY
        + cv2.THRESH_OTSU,
    )

    return threshold_image


def rotate_image(
    image: np.ndarray,
    angle: int,
) -> np.ndarray:
    """
    Görüntüyü 0, 90, 180 veya 270 derece döndürür.
    """
    if image.size == 0:
        raise ValueError(
            "Döndürülecek görüntü boş."
        )

    normalized_angle = angle % 360

    if normalized_angle == 0:
        return image.copy()

    if normalized_angle == 90:
        return cv2.rotate(
            image,
            cv2.ROTATE_90_CLOCKWISE,
        )

    if normalized_angle == 180:
        return cv2.rotate(
            image,
            cv2.ROTATE_180,
        )

    if normalized_angle == 270:
        return cv2.rotate(
            image,
            cv2.ROTATE_90_COUNTERCLOCKWISE,
        )

    raise ValueError(
        "Yalnızca 0, 90, 180 ve 270 derece "
        f"desteklenir. Alınan açı: {angle}"
    )


def create_rotated_images(
    image: np.ndarray,
    rotation_angles: tuple[int, ...] = (
        0,
        90,
        180,
        270,
    ),
) -> dict[str, np.ndarray]:
    """
    OCR için görüntünün farklı yönlerdeki kopyalarını üretir.
    """
    if not rotation_angles:
        raise ValueError(
            "En az bir döndürme açısı verilmelidir."
        )

    rotated_images: dict[str, np.ndarray] = {}
    processed_angles: set[int] = set()

    for angle in rotation_angles:
        normalized_angle = angle % 360

        if normalized_angle in processed_angles:
            continue

        rotated_images[
            f"angle_{normalized_angle:03d}"
        ] = rotate_image(
            image=image,
            angle=normalized_angle,
        )

        processed_angles.add(
            normalized_angle
        )

    return rotated_images


def add_standard_variants(
    variants: dict[str, np.ndarray],
    prefix: str,
    image: np.ndarray,
) -> None:
    """
    Normal ve orta kalite görüntüler için temel OCR
    varyantlarını sözlüğe ekler.
    """
    clahe_image = apply_clahe(
        image
    )

    variants[
        f"{prefix}_original_color"
    ] = image

    variants[
        f"{prefix}_sharpened_color"
    ] = apply_sharpening(
        image
    )

    variants[
        f"{prefix}_unsharp_mask"
    ] = apply_unsharp_mask(
        image
    )

    variants[
        f"{prefix}_clahe"
    ] = clahe_image

    variants[
        f"{prefix}_clahe_sharpened"
    ] = apply_sharpening(
        clahe_image
    )

    variants[
        f"{prefix}_otsu_threshold"
    ] = apply_otsu_threshold(
        image
    )


def add_blurry_image_variants(
    variants: dict[str, np.ndarray],
    prefix: str,
    image: np.ndarray,
) -> None:
    """
    Bulanık ve düşük ışıklı görüntüler için ek OCR
    varyantlarını sözlüğe ekler.
    """
    variants[
        f"{prefix}_strong_unsharp"
    ] = apply_strong_unsharp_mask(
        image
    )

    variants[
        f"{prefix}_bilateral_clahe"
    ] = apply_bilateral_clahe(
        image
    )

    variants[
        f"{prefix}_adaptive_threshold"
    ] = apply_adaptive_threshold(
        image
    )


def create_ocr_variants(
    image_input: ImageInput,
    scale_factor: float = 2.0,
    rotation_angles: tuple[int, ...] = (
        0,
        90,
        180,
        270,
    ),
    blur_threshold: float = (
        DEFAULT_BLUR_THRESHOLD
    ),
    blurry_scale_factor: float = (
        BLURRY_IMAGE_SCALE_FACTOR
    ),
) -> dict[str, np.ndarray]:
    """
    Döndürme, büyütme ve görüntü iyileştirme
    varyantlarını oluşturur.

    Normal görüntüler:
    - Her açı için 2x büyütme
    - original
    - sharpen
    - unsharp
    - CLAHE
    - CLAHE + sharpen
    - Otsu

    Bulanık görüntüler:
    - Yukarıdaki varyantlara ek olarak
    - strong unsharp
    - bilateral + CLAHE
    - adaptive threshold
    - Seçili 3x büyütme varyantları
    """
    if blur_threshold < 0:
        raise ValueError(
            "blur_threshold negatif olamaz."
        )

    if blurry_scale_factor <= 0:
        raise ValueError(
            "blurry_scale_factor sıfırdan büyük olmalıdır."
        )

    original_image = load_ocr_image(
        image_input=image_input,
    )

    blur_score = calculate_blur_score(
        original_image
    )

    is_blurry = (
        blur_score < blur_threshold
    )

    print(
        f"OCR blur skoru: {blur_score:.2f}"
    )
    print(
        "OCR görüntü durumu: "
        + (
            "Bulanık / özel preprocessing uygulanacak"
            if is_blurry
            else "Normal"
        )
    )

    rotated_images = create_rotated_images(
        image=original_image,
        rotation_angles=rotation_angles,
    )

    variants: dict[str, np.ndarray] = {}

    for angle_name, rotated_image in (
        rotated_images.items()
    ):
        upscaled_image = upscale_image(
            image=rotated_image,
            scale_factor=scale_factor,
        )

        standard_prefix = (
            f"{angle_name}_scale_{scale_factor:g}x"
        )

        add_standard_variants(
            variants=variants,
            prefix=standard_prefix,
            image=upscaled_image,
        )

        if not is_blurry:
            continue

        add_blurry_image_variants(
            variants=variants,
            prefix=standard_prefix,
            image=upscaled_image,
        )

        if blurry_scale_factor == scale_factor:
            continue

        larger_image = upscale_image(
            image=rotated_image,
            scale_factor=blurry_scale_factor,
        )

        larger_prefix = (
            f"{angle_name}_scale_"
            f"{blurry_scale_factor:g}x"
        )

        # 3x ölçekte bütün varyantları üretmek CPU'da
        # çok yavaş olacağından yalnızca en faydalı
        # dört varyant çalıştırılır.
        variants[
            f"{larger_prefix}_original_color"
        ] = larger_image

        variants[
            f"{larger_prefix}_clahe"
        ] = apply_clahe(
            larger_image
        )

        variants[
            f"{larger_prefix}_strong_unsharp"
        ] = apply_strong_unsharp_mask(
            larger_image
        )

        variants[
            f"{larger_prefix}_bilateral_clahe"
        ] = apply_bilateral_clahe(
            larger_image
        )

    return variants


def normalize_candidate_text(
    text: str,
) -> str:
    """
    OCR metnini aday karşılaştırması için temizler.
    """
    normalized_text = text.strip().casefold()

    characters_to_remove = {
        "[",
        "]",
        "{",
        "}",
        "(",
        ")",
        "|",
        "\\",
    }

    for character in characters_to_remove:
        normalized_text = normalized_text.replace(
            character,
            "",
        )

    normalized_text = normalized_text.replace(
        "-",
        " ",
    )

    normalized_text = " ".join(
        normalized_text.split()
    )

    return normalized_text


def run_ocr_on_variant(
    reader: easyocr.Reader,
    image: np.ndarray,
) -> list[Any]:
    """
    Tek bir preprocessing varyantında EasyOCR çalıştırır.
    """
    return reader.readtext(
        image,
        detail=1,
        paragraph=False,
    )


def extract_candidates_from_results(
    ocr_results: list[Any],
    variant_name: str,
    minimum_confidence: float = 0.0,
) -> list[OCRCandidate]:
    """
    EasyOCR sonuçlarından OCRCandidate nesneleri üretir.
    """
    candidates: list[OCRCandidate] = []

    for result in ocr_results:
        if len(result) < 3:
            continue

        _, text, confidence = result

        confidence = float(
            confidence
        )

        if confidence < minimum_confidence:
            continue

        normalized_text = normalize_candidate_text(
            str(text)
        )

        if not normalized_text:
            continue

        candidates.append(
            OCRCandidate(
                text=normalized_text,
                confidence=confidence,
                variant_name=variant_name,
                is_combined=False,
            )
        )

    return candidates


def should_combine_candidates(
    first_candidate: OCRCandidate,
    second_candidate: OCRCandidate,
) -> bool:
    """
    Yalnızca bölünmüş kısa marka parçalarını birleştirir.

    Örnek:
        a + ferin -> aferin
    """
    first_text = first_candidate.text.replace(
        " ",
        "",
    )

    second_text = second_candidate.text.replace(
        " ",
        "",
    )

    if not first_text:
        return False

    if not second_text:
        return False

    if not first_text.isalpha():
        return False

    if not second_text.isalpha():
        return False

    first_is_short_prefix = (
        1 <= len(first_text) <= 2
    )

    second_has_name_length = (
        3 <= len(second_text) <= 20
    )

    return (
        first_is_short_prefix
        and second_has_name_length
    )


def create_adjacent_candidates(
    candidates: list[OCRCandidate],
) -> list[OCRCandidate]:
    """
    Anlamlı komşu OCR parçalarını birleştirir.
    """
    combined_candidates: list[
        OCRCandidate
    ] = []

    for index in range(
        len(candidates) - 1
    ):
        first_candidate = candidates[index]
        second_candidate = candidates[index + 1]

        if not should_combine_candidates(
            first_candidate=first_candidate,
            second_candidate=second_candidate,
        ):
            continue

        combined_text = (
            first_candidate.text.replace(
                " ",
                "",
            )
            + second_candidate.text.replace(
                " ",
                "",
            )
        )

        combined_confidence = (
            first_candidate.confidence
            + second_candidate.confidence
        ) / 2

        combined_candidates.append(
            OCRCandidate(
                text=combined_text,
                confidence=combined_confidence,
                variant_name=(
                    first_candidate.variant_name
                ),
                is_combined=True,
            )
        )

    return combined_candidates


def deduplicate_candidates(
    candidates: list[OCRCandidate],
) -> list[OCRCandidate]:
    """
    Aynı metne sahip adaylardan en yüksek güven
    skoruna sahip olanı korur.
    """
    best_candidates: dict[
        str,
        OCRCandidate,
    ] = {}

    for candidate in candidates:
        existing_candidate = (
            best_candidates.get(
                candidate.text
            )
        )

        if existing_candidate is None:
            best_candidates[
                candidate.text
            ] = candidate
            continue

        if (
            candidate.confidence
            > existing_candidate.confidence
        ):
            best_candidates[
                candidate.text
            ] = candidate

    return sorted(
        best_candidates.values(),
        key=lambda candidate: (
            candidate.confidence
        ),
        reverse=True,
    )


def save_ocr_variants(
    variants: dict[str, np.ndarray],
    output_directory: str | Path,
) -> dict[str, Path]:
    """
    OCR preprocessing varyantlarını kaydeder.
    """
    output_directory = Path(
        output_directory
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    saved_paths: dict[str, Path] = {}

    for variant_name, variant_image in (
        variants.items()
    ):
        output_path = (
            output_directory
            / f"{variant_name}.jpg"
        )

        success = cv2.imwrite(
            str(output_path),
            variant_image,
        )

        if not success:
            raise IOError(
                "OCR varyantı kaydedilemedi: "
                f"{output_path}"
            )

        saved_paths[
            variant_name
        ] = output_path

    return saved_paths


def run_ocr_pipeline(
    reader: easyocr.Reader,
    image_input: ImageInput,
    scale_factor: float = 2.0,
    minimum_confidence: float = 0.0,
    rotation_angles: tuple[int, ...] = (
        0,
        90,
        180,
        270,
    ),
    save_preprocessed_images: bool = False,
    output_directory: str | Path | None = None,
    blur_threshold: float = (
        DEFAULT_BLUR_THRESHOLD
    ),
    blurry_scale_factor: float = (
        BLURRY_IMAGE_SCALE_FACTOR
    ),
) -> OCRPipelineResult:
    """
    Çoklu preprocessing ve OCR pipeline'ını çalıştırır.

    Mevcut çağrılarla geriye dönük uyumludur.
    Bulanık görüntüler otomatik olarak belirlenir ve
    özel preprocessing varyantları yalnızca gerektiğinde
    devreye girer.
    """
    variants = create_ocr_variants(
        image_input=image_input,
        scale_factor=scale_factor,
        rotation_angles=rotation_angles,
        blur_threshold=blur_threshold,
        blurry_scale_factor=(
            blurry_scale_factor
        ),
    )

    saved_variant_paths: dict[
        str,
        Path,
    ] = {}

    if save_preprocessed_images:
        if output_directory is None:
            raise ValueError(
                "save_preprocessed_images=True olduğunda "
                "output_directory verilmelidir."
            )

        saved_variant_paths = save_ocr_variants(
            variants=variants,
            output_directory=output_directory,
        )

    variant_results: dict[
        str,
        list[Any],
    ] = {}

    all_candidates: list[
        OCRCandidate
    ] = []

    print(
        f"OCR varyant sayısı: {len(variants)}"
    )

    for variant_name, variant_image in (
        variants.items()
    ):
        ocr_results = run_ocr_on_variant(
            reader=reader,
            image=variant_image,
        )

        variant_results[
            variant_name
        ] = ocr_results

        variant_candidates = (
            extract_candidates_from_results(
                ocr_results=ocr_results,
                variant_name=variant_name,
                minimum_confidence=(
                    minimum_confidence
                ),
            )
        )

        combined_candidates = (
            create_adjacent_candidates(
                candidates=variant_candidates,
            )
        )

        all_candidates.extend(
            variant_candidates
        )

        all_candidates.extend(
            combined_candidates
        )

    unique_candidates = deduplicate_candidates(
        candidates=all_candidates,
    )

    return OCRPipelineResult(
        candidates=unique_candidates,
        variant_results=variant_results,
        saved_variant_paths=saved_variant_paths,
    )


def get_candidate_texts(
    pipeline_result: OCRPipelineResult,
) -> list[str]:
    """
    OCRPipelineResult içindeki adayların yalnızca
    metinlerini döndürür.
    """
    return [
        candidate.text
        for candidate in pipeline_result.candidates
    ]