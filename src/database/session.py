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
_database_path: Path | None = None


def get_sqlite_url(database_path: Path) -> str:
    """Build a SQLite connection URL."""
    return f"sqlite:///{database_path.resolve().as_posix()}"


def init_engine(
    database_path: Path,
    *,
    echo: bool = False,
) -> Engine:
    """
    Create the SQLite engine and session factory.

    Reuse the existing engine for the same database path.
    Create the parent directory for the database file when it does not exist.
    """
    global _engine, _SessionLocal, _database_path

    database_path = Path(database_path).resolve()
    database_path.parent.mkdir(parents=True, exist_ok=True)

    if _engine is not None and _database_path == database_path:
        return _engine

    if _engine is not None:
        _engine.dispose()
        _engine = None
        _SessionLocal = None
        _database_path = None

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
    _database_path = database_path
    _SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    return engine


def create_tables(engine: Engine | None = None) -> None:
    """Create the Medicine table if it does not exist."""
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
    """Reset the engine for tests or reconfiguration."""
    global _engine, _SessionLocal, _database_path

    if _engine is not None:
        _engine.dispose()

    _engine = None
    _SessionLocal = None
    _database_path = None
