"""Barcode reading and catalog key normalization."""

from src.barcode.decoder import (
    DecodedBarcode,
    decode_barcode_texts,
    decode_barcodes,
)
from src.barcode.normalize import barcode_lookup_keys, is_plausible_barcode, normalize_barcode

__all__ = [
    "DecodedBarcode",
    "decode_barcode_texts",
    "decode_barcodes",
    "barcode_lookup_keys",
    "is_plausible_barcode",
    "normalize_barcode",
]
