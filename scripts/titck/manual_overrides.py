"""Manual corrections after TITCK matching for known medicines."""

from __future__ import annotations

MANUAL_OVERRIDES: dict[str, dict[str, str]] = {
    # TITCK has no base NUROFEN tablet record; use an ibuprofen OTC reference.
    "MED011": {
        "active_ingredient": "Ibuprofen",
        "dosage": "200 mg",
        "form": "Tablet",
    },
    # Food supplement; an exact record may not exist in the TITCK medicine list.
    "MED031": {
        "active_ingredient": "Vitamin C / Zinc / Vitamin D3",
        "dosage": "Food supplement",
        "form": "Saşe",
        "category": "Vitamin ve Mineral",
    },
    # Multivitamin variant outside SKRS coverage.
    "MED030": {
        "active_ingredient": "Multivitamin / Mineral",
        "dosage": "Combined tablet",
        "form": "Film Kaplı Tablet",
    },
}

# Known incorrect fields; preserved after TITCK enrichment as well.
ROW_CORRECTIONS: dict[str, dict[str, str]] = {
    "MED022": {
        "dosage": "50 mg",
        "form": "Film Kaplı Tablet",
    },
    "MED023": {
        "dosage": "680 mg",
        "form": "Çiğnenebilir Tablet",
    },
    "MED084": {"category": "Nöroloji"},
    "MED085": {"category": "Nöroloji"},
    "MED086": {"category": "Nöroloji"},
    "MED105": {
        "category": "Genel",
        "form": "Krem",
    },
    "MED106": {"category": "Genel"},
}


def apply_manual_overrides(row: dict[str, str]) -> dict[str, str]:
    medicine_id = row.get("medicine_id", "")
    updated = dict(row)

    correction = ROW_CORRECTIONS.get(medicine_id)
    if correction:
        updated.update(correction)

    override = MANUAL_OVERRIDES.get(medicine_id)
    if not override:
        return updated

    force_ids = {"MED011"}
    for key, value in override.items():
        current = str(updated.get(key, "")).strip()
        if medicine_id in force_ids or not current or current.startswith("VERIFY_FROM_OFFICIAL"):
            updated[key] = value
    return updated
