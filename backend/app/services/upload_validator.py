import imghdr
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

    if (
        content_type is not None
        and content_type not in ALLOWED_CONTENT_TYPES
    ):
        raise UnsupportedMediaTypeError(
            f"Desteklenmeyen content-type: {content_type}"
        )

    return suffix


def validate_image_bytes(
    file_bytes: bytes,
    *,
    suffix: str,
) -> None:
    """Dosya imzasini kontrol ederek sahte uzanti yuklemelerini reddeder."""
    if not file_bytes:
        raise UnsupportedMediaTypeError("Bos dosya yuklenemez.")

    if suffix == ".webp":
        if not (
            len(file_bytes) >= 12
            and file_bytes[:4] == b"RIFF"
            and file_bytes[8:12] == b"WEBP"
        ):
            raise UnsupportedMediaTypeError(
                "Gecersiz WEBP dosya icerigi."
            )
        return

    if suffix == ".bmp":
        if len(file_bytes) < 2 or file_bytes[:2] != b"BM":
            raise UnsupportedMediaTypeError(
                "Gecersiz BMP dosya icerigi."
            )
        return

    detected_type = imghdr.what(None, h=file_bytes)

    if detected_type is None:
        raise UnsupportedMediaTypeError(
            "Gecersiz gorsel dosya icerigi."
        )

    expected_type = {
        ".jpg": "jpeg",
        ".jpeg": "jpeg",
        ".png": "png",
    }.get(suffix)

    if expected_type is not None and detected_type != expected_type:
        raise UnsupportedMediaTypeError(
            "Dosya uzantisi ile icerik uyusmuyor."
        )
