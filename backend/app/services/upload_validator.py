from pathlib import Path

from backend.app.exceptions import UnsupportedMediaTypeError

ALLOWED_CONTENT_TYPES = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/bmp",
    }
)

CONTENT_TYPE_BY_SUFFIX = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
}

_JPEG_SOI = b"\xff\xd8\xff"
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def resolve_upload_suffix(
    filename: str | None,
    content_type: str | None,
) -> str:
    if filename:
        suffix = Path(filename).suffix.lower()
        if suffix:
            return suffix

    if content_type == "image/png":
        return ".png"
    if content_type == "image/webp":
        return ".webp"
    if content_type == "image/bmp":
        return ".bmp"

    return ".jpg"


def validate_upload_metadata(
    *,
    filename: str | None,
    content_type: str | None,
    allowed_extensions: tuple[str, ...],
) -> str:
    suffix = resolve_upload_suffix(filename, content_type)

    if suffix not in allowed_extensions:
        raise UnsupportedMediaTypeError(
            f"Desteklenmeyen dosya uzantisi: {suffix}"
        )

    if content_type == "application/octet-stream":
        content_type = CONTENT_TYPE_BY_SUFFIX.get(suffix)

    if (
        content_type is not None
        and content_type not in ALLOWED_CONTENT_TYPES
    ):
        raise UnsupportedMediaTypeError(
            f"Desteklenmeyen content-type: {content_type}"
        )

    return suffix


def _detect_image_kind(file_bytes: bytes) -> str | None:
    """Return canonical kind (jpeg/png/webp/bmp) from magic bytes."""
    if len(file_bytes) >= 3 and file_bytes[:3] == _JPEG_SOI:
        return "jpeg"
    if len(file_bytes) >= 8 and file_bytes[:8] == _PNG_SIGNATURE:
        return "png"
    if (
        len(file_bytes) >= 12
        and file_bytes[:4] == b"RIFF"
        and file_bytes[8:12] == b"WEBP"
    ):
        return "webp"
    if len(file_bytes) >= 2 and file_bytes[:2] == b"BM":
        return "bmp"
    return None


def validate_image_bytes(
    file_bytes: bytes,
    *,
    suffix: str,
) -> None:
    """Reject spoofed extension uploads by checking the file signature."""
    if not file_bytes:
        raise UnsupportedMediaTypeError("Bos dosya yuklenemez.")

    detected_type = _detect_image_kind(file_bytes)
    if detected_type is None:
        raise UnsupportedMediaTypeError(
            "Gecersiz gorsel dosya icerigi."
        )

    expected_type = {
        ".jpg": "jpeg",
        ".jpeg": "jpeg",
        ".png": "png",
        ".webp": "webp",
        ".bmp": "bmp",
    }.get(suffix)

    if expected_type is not None and detected_type != expected_type:
        raise UnsupportedMediaTypeError(
            "Dosya uzantisi ile icerik uyusmuyor."
        )
