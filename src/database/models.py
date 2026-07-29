from __future__ import annotations

from sqlalchemy import String
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
