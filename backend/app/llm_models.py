"""Ucretsiz Gemini tier icin onaylanmis model onceligi."""

# Birincil: en iyi calisan ucretsiz Flash modeli
# Yedek: kota/limit durumunda daha hafif model
GEMINI_FREE_TIER_MODELS: tuple[str, ...] = (
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
)

DEFAULT_GEMINI_MODEL = GEMINI_FREE_TIER_MODELS[0]
