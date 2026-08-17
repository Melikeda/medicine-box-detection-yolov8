"""Approved model priority for the free Gemini tier."""

# Primary: best-performing free Flash model.
# Fallback: lighter model for quota or limit situations.
GEMINI_FREE_TIER_MODELS: tuple[str, ...] = (
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-2.0-flash",
    "gemini-2.5-flash-lite",
)

DEFAULT_GEMINI_MODEL = GEMINI_FREE_TIER_MODELS[0]
