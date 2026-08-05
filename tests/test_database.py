from pathlib import Path

from src.database.repository import (
    get_medicine_by_id,
    list_categories,
    list_medicines,
    load_medicines_from_sqlite,
    seed_medicines_from_csv,
)
from src.database.session import session_scope
from src.services.config import PipelineConfig


def test_seed_creates_expected_medicine_count(
    sample_csv_path: Path,
    sqlite_path: Path,
) -> None:
    count = seed_medicines_from_csv(
        csv_path=sample_csv_path,
        database_path=sqlite_path,
        replace_existing=True,
    )
    assert count == 8

    medicines = load_medicines_from_sqlite(sqlite_path)
    assert len(medicines) == 8
    assert medicines[0]["medicine_id"] == "MED001"


def test_seed_upsert_updates_existing_row(
    sample_csv_path: Path,
    sqlite_path: Path,
) -> None:
    seed_medicines_from_csv(
        csv_path=sample_csv_path,
        database_path=sqlite_path,
        replace_existing=True,
    )

    updated_csv = sample_csv_path.parent / "updated.csv"
    updated_csv.write_text(
        sample_csv_path.read_text(encoding="utf-8").replace(
            "Parol,Parol,Paracetamol",
            "Parol Extra,Parol,Paracetamol",
        ),
        encoding="utf-8",
    )

    seed_medicines_from_csv(
        csv_path=updated_csv,
        database_path=sqlite_path,
        replace_existing=True,
    )

    with session_scope() as session:
        medicine = get_medicine_by_id(session, "MED001")
        assert medicine is not None
        assert medicine.medicine_name == "Parol Extra"


def test_list_and_search_medicines(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    with session_scope() as session:
        all_medicines = list_medicines(session, limit=100)
        assert len(all_medicines) == 8

        search_hits = list_medicines(
            session,
            search="ibu",
            limit=100,
        )
        names = [item.medicine_name for item in search_hits]
        assert "Ibucold" in names
        assert "Ibucold C" in names


def test_list_categories(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    with session_scope() as session:
        categories = list_categories(session)

    assert "Ağrı Kesici" in categories
    assert "Soğuk Algınlığı" in categories
    assert len(categories) >= 3
