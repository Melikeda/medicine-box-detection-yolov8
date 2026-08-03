"""Bilinen ilaçlar için TİTCK eşleşmesi sonrası manuel düzeltmeler."""

from __future__ import annotations

MANUAL_OVERRIDES: dict[str, dict[str, str]] = {
    # TİTCK'de temel NUROFEN tablet kaydı yok; ibuprofen OTC referansı.
    "MED011": {
        "active_ingredient": "Ibuprofen",
        "dosage": "200 mg",
        "form": "Tablet",
    },
    # Gıda takviyesi — TİTCK ilaç listesinde birebir kayıt olmayabilir.
    "MED031": {
        "active_ingredient": "Vitamin C / Zinc / Vitamin D3",
        "dosage": "Food supplement",
        "form": "Saşe",
        "category": "Vitamin ve Mineral",
    },
    # Multivitamin — SKRS kapsamı dışı varyant.
    "MED030": {
        "active_ingredient": "Multivitamin / Mineral",
        "dosage": "Combined tablet",
        "form": "Film Kaplı Tablet",
    },
}


def apply_manual_overrides(row: dict[str, str]) -> dict[str, str]:
    override = MANUAL_OVERRIDES.get(row.get("medicine_id", ""))
    if not override:
        return row
    updated = dict(row)
    force_ids = {"MED011"}
    medicine_id = row.get("medicine_id", "")
    for key, value in override.items():
        current = str(updated.get(key, "")).strip()
        if medicine_id in force_ids or not current or current.startswith("VERIFY_FROM_OFFICIAL"):
            updated[key] = value
    return updated
