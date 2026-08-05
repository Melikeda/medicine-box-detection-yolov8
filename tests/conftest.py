from __future__ import annotations

from pathlib import Path

import pytest

from src.database.repository import seed_medicines_from_csv
from src.database.session import reset_engine
from src.services.config import PipelineConfig


SAMPLE_CSV = """medicine_id,medicine_name,brand_name,active_ingredient,dosage,form,category
MED001,Parol,Parol,Paracetamol,500 mg,Tablet,Ağrı Kesici
MED011,Nurofen,Nurofen,Ibuprofen,VERIFY_FROM_OFFICIAL_LEAFLET,VERIFY_FROM_OFFICIAL_LEAFLET,Ağrı Kesici
MED012,Nurofen Cold & Flu,Nurofen,"Ibuprofen / Pseudoephedrine Hydrochloride","200 mg / 30 mg",Film Coated Tablet,Soğuk Algınlığı
MED033,Ibucold C,Ibucold C,Ibuprofen + Pseudoephedrine Hydrochloride + Ascorbic Acid,200 mg / 30 mg / 300 mg,Film Coated Tablet,Soğuk Algınlığı
MED034,Ibucold,Ibucold,Ibuprofen + Pseudoephedrine Hydrochloride,200 mg / 30 mg,Film Coated Tablet,Soğuk Algınlığı
MED032,Biteral,Biteral,Metronidazole / Ornidazole,500 MG,Film Coated Tablet,Antibiyotik
MED036,Levopront,Levopront,Levodropropizine,60 mg,Tablet,Öksürük İlacı
MED038,Parafon,Parafon,Paracetamol + Chlorzoxazone,250 mg / 300 mg,Tablet,Kas-İskelet
"""


@pytest.fixture()
def sample_csv_path(tmp_path: Path) -> Path:
    csv_path = tmp_path / "medicines.csv"
    csv_path.write_text(SAMPLE_CSV, encoding="utf-8")
    return csv_path


@pytest.fixture()
def sqlite_path(tmp_path: Path) -> Path:
    return tmp_path / "test_medicines.db"


@pytest.fixture()
def seeded_pipeline_config(
    sample_csv_path: Path,
    sqlite_path: Path,
) -> PipelineConfig:
    reset_engine()
    seed_medicines_from_csv(
        csv_path=sample_csv_path,
        database_path=sqlite_path,
        replace_existing=True,
    )
    return PipelineConfig(
        medicines_csv_path=sample_csv_path,
        sqlite_path=sqlite_path,
        use_sqlite=True,
    )


@pytest.fixture(autouse=True)
def _reset_db_engine() -> None:
    reset_engine()
    yield
    reset_engine()
