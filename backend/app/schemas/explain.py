from pydantic import BaseModel, Field


class ExplainRequestSchema(BaseModel):
    """LLM ilaç açıklaması isteği."""

    medicine_id: str = Field(min_length=1, max_length=64)
    locale: str = Field(default="tr", min_length=2, max_length=8)


class MedicineExplanationSchema(BaseModel):
    """Yapılandırılmış ilaç açıklaması (kullanıcı odaklı)."""

    summary: str
    usage: str = ""
    commonUses: list[str] = Field(default_factory=list)
    activeIngredient: str | None = None
    dose: str | None = None
    form: str | None = None
    category: str | None = None
    warnings: list[str] = Field(default_factory=list)
    disclaimer: str = ""


class ExplainResponseSchema(BaseModel):
    """LLM ilaç açıklaması yanıtı."""

    success: bool = True
    medicine_id: str
    medicine_name: str
    explanation: str
    summary: str = ""
    usage: str = ""
    commonUses: list[str] = Field(default_factory=list)
    activeIngredient: str | None = None
    dose: str | None = None
    form: str | None = None
    category: str | None = None
    warnings: list[str] = Field(default_factory=list)
    structured: MedicineExplanationSchema | None = None
    disclaimer: str
    cached: bool = False
    provider: str
    model: str


class ExplainInfoSchema(BaseModel):
    """Explain endpoint bilgisi."""

    endpoint: str
    method: str = "POST"
    llm_enabled: bool
    llm_configured: bool
    ready: bool = False
    status_message: str = ""
    provider: str
    model: str
    rate_limit_enabled: bool = True
    rate_limit_explain_per_minute: int | None = None
    cache_enabled: bool = True
