from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from src.ocr.ocr_reader import OCRReader


ImageInput = str | Path | np.ndarray

DEFAULT_BLUR_THRESHOLD = 80.0
BLURRY_IMAGE_SCALE_FACTOR = 3.0


@dataclass
class OCRCandidate:
    """
    Represents a single text candidate produced from an OCR result.
    """

    text: str
    confidence: float
    variant_name: str
    is_combined: bool = False


@dataclass
class OCRPipelineResult:
    """
    Represents a multi-step OCR pipeline result.
    """

    candidates: list[OCRCandidate]
    variant_results: dict[str, list[Any]]
    saved_variant_paths: dict[str, Path]
    variants_processed: int = 0
    variants_total: int = 0
    early_exit: bool = False


def load_ocr_image(
    image_input: ImageInput,
) -> np.ndarray:
    """
    Load the image for OCR.

    Supported inputs:
    - str file path
    - Path file path
    - OpenCV numpy.ndarray image
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
    Upscale the image with INTER_CUBIC before OCR.
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
    Convert the image to grayscale.
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
    Calculate the image sharpness score using Laplacian variance.

    General interpretation:
    - Higher score: sharper image
    - Lower score: blurrier image

    The threshold can vary by image size and camera.
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
    Emphasize text edges in the image.
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
    Apply the standard unsharp mask.
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
    Apply a stronger unsharp mask for blurry text.

    It cannot recover severe motion blur; it only strengthens preserved edge information.
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
    Increase local contrast in low-light and low-contrast images.
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
    """Try to reduce noise while preserving edges."""
    return cv2.bilateralFilter(
        image,
        d=7,
        sigmaColor=55,
        sigmaSpace=55,
    )


def apply_bilateral_clahe(
    image: np.ndarray,
) -> np.ndarray:
    """Reduce noise first, then increase local contrast."""
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
    Apply adaptive thresholding based on variable lighting across image regions.
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
    """Create a binary image with Otsu thresholding."""
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
    """Rotate the image by 0, 90, 180, or 270 degrees."""
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
    """Create image copies at different orientations for OCR."""
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


def add_minimal_variants(
    variants: dict[str, np.ndarray],
    prefix: str,
    image: np.ndarray,
) -> None:
    """Lightweight variant set for fast OCR mode, with two variants per angle."""
    variants[f"{prefix}_original_color"] = image
    variants[f"{prefix}_sharpened_color"] = apply_sharpening(
        image
    )


def add_standard_variants(
    variants: dict[str, np.ndarray],
    prefix: str,
    image: np.ndarray,
) -> None:
    """
    Add the base OCR variants for normal and medium-quality images to the dictionary.
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
    Add extra OCR variants for blurry and low-light images.
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
    limited_variants: bool = False,
) -> dict[str, np.ndarray]:
    """
    Build rotated, upscaled, and enhanced image variants.

    Normal images:
    - 2x upscaling for each angle

    Blurry images:
    - Additional variants on top of the above
    - Selected 3x upscaling variants
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

        if limited_variants:
            add_minimal_variants(
                variants=variants,
                prefix=standard_prefix,
                image=upscaled_image,
            )
            continue

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

        # Running every variant at 3x scale is very slow on CPU, so only
        # the four most useful variants are processed.
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
    Clean OCR text for candidate comparison.
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
    reader: OCRReader,
    image: np.ndarray,
) -> list[Any]:
    """
    Run OCR on a single preprocessing variant.

    Uses EasyOCR readtext(image, detail=1, paragraph=False).
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
    """Build OCRCandidate objects from EasyOCR results."""
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
    Combine only split short brand fragments.

    Example:
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
    """Combine meaningful neighboring OCR fragments."""
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
    Keep the highest-confidence candidate for each repeated text value.
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
    """Save OCR preprocessing variants."""
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
    reader: OCRReader,
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
    limited_variants: bool = False,
    should_stop_after_variant: (
        Callable[[list[str]], bool] | None
    ) = None,
) -> OCRPipelineResult:
    """
    Run the multi-preprocessing OCR pipeline.

    Compatible with existing callers. Blurry images are detected automatically,
    and special preprocessing variants are used only when needed.
    """
    variants = create_ocr_variants(
        image_input=image_input,
        scale_factor=scale_factor,
        rotation_angles=rotation_angles,
        blur_threshold=blur_threshold,
        blurry_scale_factor=(
            blurry_scale_factor
        ),
        limited_variants=limited_variants,
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

    total_variants = len(variants)
    variants_processed = 0
    early_exit = False

    for index, (variant_name, variant_image) in enumerate(
        variants.items(),
        start=1,
    ):
        print(
            f"OCR isleniyor [{index}/{total_variants}]: "
            f"{variant_name}",
            flush=True,
        )

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

        variants_processed = index

        if should_stop_after_variant is not None:
            unique_so_far = deduplicate_candidates(
                candidates=all_candidates,
            )
            candidate_texts = [
                candidate.text for candidate in unique_so_far
            ]
            if should_stop_after_variant(candidate_texts):
                print(
                    f"OCR erken cikis: {index}/{total_variants} "
                    "varyant sonrasi guvenilir eslesme",
                    flush=True,
                )
                early_exit = True
                break

    unique_candidates = deduplicate_candidates(
        candidates=all_candidates,
    )

    return OCRPipelineResult(
        candidates=unique_candidates,
        variant_results=variant_results,
        saved_variant_paths=saved_variant_paths,
        variants_processed=variants_processed,
        variants_total=total_variants,
        early_exit=early_exit,
    )


def get_candidate_texts(
    pipeline_result: OCRPipelineResult,
) -> list[str]:
    """
    Return only the candidate texts from an OCRPipelineResult.
    """
    return [
        candidate.text
        for candidate in pipeline_result.candidates
    ]
