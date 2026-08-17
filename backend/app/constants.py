"""API constants."""

MEDICAL_DISCLAIMER = (
    "This app does not give medical advice. "
    "Confirm details with the official leaflet or a pharmacist."
)

LLM_EXPLANATION_DISCLAIMER = (
    "This is general medicine information and does not replace personal medical advice. "
    "Ask a doctor or pharmacist whether this medicine is appropriate for you."
)

LLM_EXPLANATION_DISCLAIMER_TR = (
    "Bu bilgiler genel ilaç bilgisidir ve kişisel tıbbi öneri yerine geçmez. "
    "İlacın sizin için uygun olup olmadığını doktorunuza veya eczacınıza danışın."
)


def disclaimer_for_locale(locale: str) -> str:
    if (locale or "tr").strip().lower().startswith("en"):
        return LLM_EXPLANATION_DISCLAIMER
    return LLM_EXPLANATION_DISCLAIMER_TR
