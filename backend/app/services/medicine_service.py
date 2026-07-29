from __future__ import annotations

from pathlib import Path

from src.database.repository import (
    count_medicines,
    get_medicine_by_id,
    list_categories,
    list_medicines,
)
from src.database.session import (
    create_tables,
    init_engine,
    session_scope,
)
from src.services.config import PipelineConfig


class MedicineQueryService:
    """SQLite üzerinden ilaç listeleme ve detay sorgusu."""

    def __init__(
        self,
        *,
        sqlite_path: Path,
        source: str = "sqlite",
    ) -> None:
        self.sqlite_path = Path(sqlite_path)
        self.source = source
        init_engine(self.sqlite_path)
        create_tables()

    @classmethod
    def from_pipeline_config(
        cls,
        config: PipelineConfig,
    ) -> MedicineQueryService:
        return cls(
            sqlite_path=config.sqlite_path,
            source="sqlite" if config.use_sqlite else "csv",
        )

    def list_medicines(
        self,
        *,
        search: str | None = None,
        category: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, str]], int]:
        with session_scope() as session:
            total = count_medicines(
                session,
                search=search,
                category=category,
            )
            medicines = list_medicines(
                session,
                search=search,
                category=category,
                limit=limit,
                offset=offset,
            )
            return (
                [medicine.to_dict() for medicine in medicines],
                total,
            )

    def get_medicine(
        self,
        medicine_id: str,
    ) -> dict[str, str] | None:
        with session_scope() as session:
            medicine = get_medicine_by_id(session, medicine_id)
            if medicine is None:
                return None
            return medicine.to_dict()

    def list_categories(self) -> list[str]:
        with session_scope() as session:
            return list_categories(session)
