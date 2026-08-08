from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


class Medicine(Base):
    """İlaç kaydı — CSV alanlarıyla birebir uyumlu."""

    __tablename__ = "medicines"

    medicine_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
    )
    medicine_name: Mapped[str] = mapped_column(String(255))
    brand_name: Mapped[str] = mapped_column(
        String(255),
        default="",
    )
    active_ingredient: Mapped[str] = mapped_column(
        String(512),
        default="",
    )
    dosage: Mapped[str] = mapped_column(
        String(128),
        default="",
    )
    form: Mapped[str] = mapped_column(
        String(128),
        default="",
    )
    category: Mapped[str] = mapped_column(
        String(128),
        default="",
    )

    def to_dict(self) -> dict[str, str]:
        """RapidFuzz / API için sözlük formuna çevirir."""
        return {
            "medicine_id": self.medicine_id,
            "medicine_name": self.medicine_name,
            "brand_name": self.brand_name,
            "active_ingredient": self.active_ingredient,
            "dosage": self.dosage,
            "form": self.form,
            "category": self.category,
        }


class Scan(Base):
    """Sunucu taraflı tarama geçmişi kaydı (auth yok — global liste)."""

    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    detection_count: Mapped[int] = mapped_column(Integer, default=0)
    matched_count: Mapped[int] = mapped_column(Integer, default=0)
    preview_label: Mapped[str] = mapped_column(String(255), default="")
    filename: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ocr_mode: Mapped[str] = mapped_column(String(32), default="fast")
    client_device_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        default=None,
    )
    response_json: Mapped[dict[str, Any]] = mapped_column(JSON)

    def to_list_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "detection_count": self.detection_count,
            "matched_count": self.matched_count,
            "preview_label": self.preview_label,
            "filename": self.filename,
            "ocr_mode": self.ocr_mode,
            "client_device_id": self.client_device_id,
        }

    def to_detail_dict(self) -> dict[str, Any]:
        detail = self.to_list_dict()
        detail["response"] = self.response_json
        return detail

