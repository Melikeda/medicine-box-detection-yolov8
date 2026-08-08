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

    _instance: MedicineQueryService | None = None

    def __init__(
        self,
        *,
        sqlite_path: Path,
        source: str = "sqlite",
    ) -> None:
        self.sqlite_path = Path(sqlite_path).resolve()
        self.source = source
        init_engine(self.sqlite_path)
        create_tables()

    @classmethod
    def from_pipeline_config(
        cls,
        config: PipelineConfig,
    ) -> MedicineQueryService:
        return cls.get_instance(
            sqlite_path=config.sqlite_path,
            source="sqlite" if config.use_sqlite else "csv",
        )

    @classmethod
    def get_instance(
        cls,
        *,
        sqlite_path: Path,
        source: str = "sqlite",
    ) -> MedicineQueryService:
        """Aynı DB yolu için tek servis örneği döndürür."""
        resolved = Path(sqlite_path).resolve()
        if (
            cls._instance is None
            or cls._instance.sqlite_path != resolved
            or cls._instance.source != source
        ):
            cls._instance = cls(
                sqlite_path=resolved,
                source=source,
            )
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Test veya yeniden yapılandırma için servis singleton'ını sıfırlar."""
        cls._instance = None

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
