from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.database.models import Base

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_sqlite_url(database_path: Path) -> str:
    """SQLite connection URL üretir."""
    return f"sqlite:///{database_path.resolve().as_posix()}"


def init_engine(
    database_path: Path,
    *,
    echo: bool = False,
) -> Engine:
    """
    SQLite engine ve session factory oluşturur.

    Veritabanı dosyasının bulunduğu klasör yoksa oluşturulur.
    """
    global _engine, _SessionLocal

    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(
        get_sqlite_url(database_path),
        echo=echo,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    _engine = engine
    _SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    return engine


def create_tables(engine: Engine | None = None) -> None:
    """Medicine tablosunu oluşturur (yoksa)."""
    active_engine = engine or _engine

    if active_engine is None:
        raise RuntimeError(
            "SQLite engine henüz başlatılmadı. "
            "Önce init_engine() çağırın."
        )

    Base.metadata.create_all(bind=active_engine)


def get_session_factory() -> sessionmaker[Session]:
    if _SessionLocal is None:
        raise RuntimeError(
            "SQLite session factory henüz başlatılmadı. "
            "Önce init_engine() çağırın."
        )
    return _SessionLocal


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Transaction-safe session context manager."""
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_engine() -> None:
    """Test veya yeniden yapılandırma için engine'i sıfırlar."""
    global _engine, _SessionLocal

    if _engine is not None:
        _engine.dispose()

    _engine = None
    _SessionLocal = None
