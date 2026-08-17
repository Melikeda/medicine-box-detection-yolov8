"""
Decode a medicine-box barcode with zxing-cpp (src.barcode).

Run:
    python -m examples.barcode.step_01_decode_barcode
    python -m examples.barcode.step_01_decode_barcode --image path/to/photo.jpg
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2

from src.barcode.decoder import decode_barcodes


def main() -> None:
    parser = argparse.ArgumentParser(description="Decode barcodes in an image")
    parser.add_argument(
        "--image",
        type=Path,
        default=None,
        help="Photo path (optional; generates a sample EAN-13 if omitted)",
    )
    args = parser.parse_args()

    if args.image is None:
        from io import BytesIO

        from barcode import EAN13
        from barcode.writer import ImageWriter
        import numpy as np

        buffer = BytesIO()
        ean = EAN13("869952209047", writer=ImageWriter())
        ean.write(buffer, options={"write_text": False, "quiet_zone": 6.5})
        array = np.frombuffer(buffer.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        print(f"Ornek EAN-13 uretildi: {ean.get_fullcode()}")
    else:
        image = cv2.imread(str(args.image))
        if image is None:
            raise SystemExit(f"Gorsel okunamadi: {args.image}")

    decoded = decode_barcodes(image)
    if not decoded:
        print("Barkod bulunamadi.")
        return

    print(f"Okunan barkod sayisi: {len(decoded)}")
    for item in decoded:
        print(f"- {item.normalized} ({item.format}) raw={item.text}")


if __name__ == "__main__":
    main()
