from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.config import ApiSettings, get_api_settings
from backend.app.schemas.medicines import (
    MedicineDetailResponseSchema,
    MedicineListResponseSchema,
    MedicineSchema,
)
from backend.app.services.medicine_service import MedicineQueryService

router = APIRouter(prefix="/medicines", tags=["medicines"])


def get_medicine_service(
    settings: ApiSettings = Depends(get_api_settings),
) -> MedicineQueryService:
    return MedicineQueryService.from_pipeline_config(
        settings.create_pipeline_config()
    )


@router.get("", response_model=MedicineListResponseSchema)
async def list_medicines(
    search: str | None = Query(
        default=None,
        description="İsim, marka veya etken madde araması",
    ),
    category: str | None = Query(
        default=None,
        description="Kategori filtresi (ör. Ağrı Kesici)",
    ),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    service: MedicineQueryService = Depends(get_medicine_service),
) -> MedicineListResponseSchema:
    """İlaç listesini döndürür (SQLite)."""
    medicines, total = service.list_medicines(
        search=search,
        category=category,
        limit=limit,
        offset=offset,
    )

    return MedicineListResponseSchema(
        total=total,
        count=len(medicines),
        offset=offset,
        limit=limit,
        source=service.source,
        medicines=[
            MedicineSchema(**medicine) for medicine in medicines
        ],
    )


@router.get(
    "/{medicine_id}",
    response_model=MedicineDetailResponseSchema,
)
async def get_medicine(
    medicine_id: str,
    service: MedicineQueryService = Depends(get_medicine_service),
) -> MedicineDetailResponseSchema:
    """medicine_id ile tek ilaç kaydı döndürür."""
    medicine = service.get_medicine(medicine_id)

    if medicine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"İlaç bulunamadı: {medicine_id}",
        )

    return MedicineDetailResponseSchema(
        source=service.source,
        medicine=MedicineSchema(**medicine),
    )
