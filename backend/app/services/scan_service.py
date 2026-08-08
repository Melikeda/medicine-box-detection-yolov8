from __future__ import annotations

from pathlib import Path
from typing import Any

from src.database.repository import (
    count_scans,
    create_scan,
    delete_scan,
    get_scan_by_id,
    list_scans,
    trim_scans,
)
from src.database.session import (
    create_tables,
    init_engine,
    session_scope,
)
from src.services.config import PipelineConfig


class ScanQueryService:
    """SQLite üzerinden sunucu tarama geçmişi CRUD."""

    _instance: ScanQueryService | None = None

    def __init__(
        self,
        *,
        sqlite_path: Path,
        max_entries: int = 200,
        source: str = "sqlite",
    ) -> None:
        self.sqlite_path = Path(sqlite_path).resolve()
        self.max_entries = max_entries
        self.source = source
        init_engine(self.sqlite_path)
        create_tables()

    @classmethod
    def from_pipeline_config(
        cls,
        config: PipelineConfig,
        *,
        max_entries: int = 200,
    ) -> ScanQueryService:
        return cls.get_instance(
            sqlite_path=config.sqlite_path,
            max_entries=max_entries,
            source="sqlite" if config.use_sqlite else "csv",
        )

    @classmethod
    def get_instance(
        cls,
        *,
        sqlite_path: Path,
        max_entries: int = 200,
        source: str = "sqlite",
    ) -> ScanQueryService:
        resolved = Path(sqlite_path).resolve()
        if (
            cls._instance is None
            or cls._instance.sqlite_path != resolved
            or cls._instance.max_entries != max_entries
            or cls._instance.source != source
        ):
            cls._instance = cls(
                sqlite_path=resolved,
                max_entries=max_entries,
                source=source,
            )
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def create_scan(
        self,
        *,
        response: dict[str, Any],
        preview_label: str | None = None,
        client_device_id: str | None = None,
    ) -> dict[str, Any]:
        with session_scope() as session:
            scan = create_scan(
                session,
                response=response,
                preview_label=preview_label,
                client_device_id=client_device_id,
            )
            trim_scans(session, max_entries=self.max_entries)
            session.refresh(scan)
            return scan.to_detail_dict()

    def list_scans(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        with session_scope() as session:
            total = count_scans(session)
            scans = list_scans(
                session,
                limit=limit,
                offset=offset,
            )
            return (
                [scan.to_list_dict() for scan in scans],
                total,
            )

    def get_scan(self, scan_id: int) -> dict[str, Any] | None:
        with session_scope() as session:
            scan = get_scan_by_id(session, scan_id)
            if scan is None:
                return None
            return scan.to_detail_dict()

    def delete_scan(self, scan_id: int) -> bool:
        with session_scope() as session:
            return delete_scan(session, scan_id)
