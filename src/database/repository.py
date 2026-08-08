from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from src.database.csv_reader import load_medicines
from src.database.models import Medicine, Scan
from src.database.session import (
    create_tables,
    init_engine,
    session_scope,
)


def seed_medicines_from_csv(
    *,
    csv_path: Path,
    database_path: Path,
    replace_existing: bool = True,
) -> int:
    """
    CSV kayıtlarını SQLite'a aktarır.

    replace_existing=True ise medicine_id üzerinden upsert yapar.
    Dönüş değeri: işlenen (eklenen/güncellenen) kayıt sayısı.
    """
    medicines = load_medicines(csv_path=csv_path)

    init_engine(database_path)
    create_tables()

    with session_scope() as session:
        if replace_existing:
            for row in medicines:
                existing = session.get(
                    Medicine,
                    row["medicine_id"],
                )
                if existing is None:
                    session.add(Medicine(**_row_to_model_kwargs(row)))
                else:
                    for key, value in _row_to_model_kwargs(row).items():
                        setattr(existing, key, value)
        else:
            count = session.scalar(
                select(func.count()).select_from(Medicine)
            )
            if count and count > 0:
                return int(count)

            session.add_all(
                [
                    Medicine(**_row_to_model_kwargs(row))
                    for row in medicines
                ]
            )

    return len(medicines)


def _row_to_model_kwargs(row: dict[str, str]) -> dict[str, str]:
    return {
        "medicine_id": row.get("medicine_id", "").strip(),
        "medicine_name": row.get("medicine_name", "").strip(),
        "brand_name": row.get("brand_name", "").strip(),
        "active_ingredient": row.get(
            "active_ingredient",
            "",
        ).strip(),
        "dosage": row.get("dosage", "").strip(),
        "form": row.get("form", "").strip(),
        "category": row.get("category", "").strip(),
    }


def ensure_database_seeded(
    *,
    csv_path: Path,
    database_path: Path,
) -> int:
    """
    Veritabanını hazırlar ve CSV ile senkronize eder.

    Pipeline/API startup'ta çağrılır.
    """
    return seed_medicines_from_csv(
        csv_path=csv_path,
        database_path=database_path,
        replace_existing=True,
    )


def list_medicines(
    session: Session,
    *,
    search: str | None = None,
    category: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Medicine]:
    """İlaç listesini filtreleyerek döndürür."""
    statement = select(Medicine).order_by(Medicine.medicine_name)

    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Medicine.medicine_name.ilike(pattern),
                Medicine.brand_name.ilike(pattern),
                Medicine.active_ingredient.ilike(pattern),
            )
        )

    if category:
        statement = statement.where(
            Medicine.category.ilike(category.strip())
        )

    statement = statement.offset(max(offset, 0)).limit(
        max(1, min(limit, 500))
    )
    return list(session.scalars(statement).all())


def count_medicines(
    session: Session,
    *,
    search: str | None = None,
    category: str | None = None,
) -> int:
    """Filtrelenmiş ilaç sayısını döndürür."""
    statement = select(func.count()).select_from(Medicine)

    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Medicine.medicine_name.ilike(pattern),
                Medicine.brand_name.ilike(pattern),
                Medicine.active_ingredient.ilike(pattern),
            )
        )

    if category:
        statement = statement.where(
            Medicine.category.ilike(category.strip())
        )

    return int(session.scalar(statement) or 0)


def get_medicine_by_id(
    session: Session,
    medicine_id: str,
) -> Medicine | None:
    """medicine_id ile tek ilaç kaydı döndürür."""
    return session.get(Medicine, medicine_id.strip())


def list_categories(session: Session) -> list[str]:
    """Benzersiz kategori listesini alfabetik döndürür."""
    rows = session.scalars(
        select(Medicine.category)
        .where(Medicine.category != "")
        .distinct()
        .order_by(Medicine.category)
    ).all()
    return [str(category) for category in rows]


def load_medicines_from_sqlite(
    database_path: Path,
) -> list[dict[str, str]]:
    """
    MatchingService için tüm ilaçları dict listesi olarak yükler.
    """
    init_engine(database_path)
    create_tables()

    with session_scope() as session:
        medicines = list(
            session.scalars(
                select(Medicine).order_by(Medicine.medicine_id)
            ).all()
        )
        return [medicine.to_dict() for medicine in medicines]


def build_scan_preview_label(response: dict[str, Any]) -> str:
    """Analyze yanıtından kısa liste etiketi üretir (mobil ile uyumlu)."""
    medicines = response.get("medicines") or []
    matched_names: list[str] = []
    for item in medicines:
        if not isinstance(item, dict):
            continue
        if item.get("status") != "matched":
            continue
        name = item.get("medicine_name")
        if isinstance(name, str) and name.strip():
            matched_names.append(name.strip())
        if len(matched_names) >= 2:
            break

    summary = response.get("summary") or {}
    matched_count = int(summary.get("matched_count") or 0)
    detection_count = int(response.get("detection_count") or 0)

    if matched_names:
        suffix = (
            f" +{matched_count - len(matched_names)}"
            if matched_count > len(matched_names)
            else ""
        )
        return f"{', '.join(matched_names)}{suffix}"

    if detection_count == 0:
        return "Kutu tespit edilemedi"

    return f"{detection_count} kutu tarandi"


def create_scan(
    session: Session,
    *,
    response: dict[str, Any],
    preview_label: str | None = None,
    client_device_id: str | None = None,
) -> Scan:
    """Başarılı analyze yanıtını scans tablosuna yazar."""
    summary = response.get("summary") or {}
    scan = Scan(
        created_at=datetime.now(timezone.utc),
        detection_count=int(response.get("detection_count") or 0),
        matched_count=int(summary.get("matched_count") or 0),
        preview_label=(
            preview_label.strip()
            if isinstance(preview_label, str) and preview_label.strip()
            else build_scan_preview_label(response)
        ),
        filename=response.get("filename"),
        ocr_mode=str(response.get("ocr_mode") or "fast"),
        client_device_id=client_device_id,
        response_json=response,
    )
    session.add(scan)
    session.flush()
    return scan


def count_scans(session: Session) -> int:
    return int(
        session.scalar(select(func.count()).select_from(Scan)) or 0
    )


def list_scans(
    session: Session,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[Scan]:
    statement = (
        select(Scan)
        .order_by(Scan.created_at.desc(), Scan.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(session.scalars(statement).all())


def get_scan_by_id(session: Session, scan_id: int) -> Scan | None:
    return session.get(Scan, scan_id)


def delete_scan(session: Session, scan_id: int) -> bool:
    scan = session.get(Scan, scan_id)
    if scan is None:
        return False
    session.delete(scan)
    return True


def trim_scans(
    session: Session,
    *,
    max_entries: int,
) -> int:
    """Eski kayıtları silerek üst sınırı korur. Silinen adedi döner."""
    if max_entries < 1:
        return 0

    total = count_scans(session)
    overflow = total - max_entries
    if overflow <= 0:
        return 0

    old_ids = list(
        session.scalars(
            select(Scan.id)
            .order_by(Scan.created_at.asc(), Scan.id.asc())
            .limit(overflow)
        ).all()
    )
    for scan_id in old_ids:
        scan = session.get(Scan, scan_id)
        if scan is not None:
            session.delete(scan)
    return len(old_ids)
