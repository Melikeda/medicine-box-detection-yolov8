from pydantic import BaseModel, Field


class MedicineSchema(BaseModel):
    """Tek ilaç kaydı."""

    medicine_id: str
    medicine_name: str
    brand_name: str = ""
    active_ingredient: str = ""
    dosage: str = ""
    form: str = ""
    category: str = ""


class MedicineListResponseSchema(BaseModel):
    """İlaç listesi yanıtı."""

    success: bool = True
    total: int
    count: int
    offset: int = 0
    limit: int = 100
    source: str = "sqlite"
    medicines: list[MedicineSchema] = Field(default_factory=list)


class MedicineDetailResponseSchema(BaseModel):
    """Tek ilaç detay yanıtı."""

    success: bool = True
    source: str = "sqlite"
    medicine: MedicineSchema


class MedicineCategoriesResponseSchema(BaseModel):
    """Kategori listesi yanıtı."""

    success: bool = True
    count: int
    source: str = "sqlite"
    categories: list[str] = Field(default_factory=list)
