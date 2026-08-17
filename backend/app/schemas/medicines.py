from pydantic import BaseModel, Field


class MedicineSchema(BaseModel):
    """Single medicine record."""

    medicine_id: str
    medicine_name: str
    brand_name: str = ""
    active_ingredient: str = ""
    dosage: str = ""
    form: str = ""
    category: str = ""


class MedicineListResponseSchema(BaseModel):
    """Medicine list response."""

    success: bool = True
    total: int
    count: int
    offset: int = 0
    limit: int = 100
    source: str = "sqlite"
    medicines: list[MedicineSchema] = Field(default_factory=list)


class MedicineDetailResponseSchema(BaseModel):
    """Single medicine detail response."""

    success: bool = True
    source: str = "sqlite"
    medicine: MedicineSchema


class MedicineCategoriesResponseSchema(BaseModel):
    """Category list response."""

    success: bool = True
    count: int
    source: str = "sqlite"
    categories: list[str] = Field(default_factory=list)
