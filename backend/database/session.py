"""SQLAlchemy engine, session factory, and FastAPI dependency.

Auto-fallback: if the configured database (e.g. PostgreSQL / Supabase) is
unreachable, a local SQLite file is used instead so the app works with
zero setup.
"""
from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.config import get_settings

logger = __import__("logging").getLogger(__name__)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""


_settings = get_settings()


def _resolve_engine():
    """Return (engine, session_maker, db_label) for the active database.

    Tries the configured ``DATABASE_URL`` first; falls back to a local
    ``sqlite:///./local.db`` file when the server is unreachable.
    """
    url = _settings.database_url
    label = "configured"

    # If it already *is* SQLite, use it directly – no point probing.
    if url.startswith("sqlite"):
        eng = create_engine(url, connect_args={"check_same_thread": False}, future=True)
        SessionLocal = sessionmaker(
            bind=eng, autoflush=False, autocommit=False, expire_on_commit=False, future=True
        )
        return eng, SessionLocal, "local-sqlite"

    try:
        eng = create_engine(url, pool_pre_ping=True, pool_size=2, max_overflow=2, future=True)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        SessionLocal = sessionmaker(
            bind=eng, autoflush=False, autocommit=False, expire_on_commit=False, future=True
        )
        logger.info("Connected to configured database: %s", url.partition("://")[0])
        return eng, SessionLocal, label
    except Exception as exc:
        logger.warning(
            "Configured database unreachable (%s); falling back to local SQLite.",
            exc,
        )

    # Fallback: local SQLite file
    db_path = Path(__file__).resolve().parent.parent.parent / "local.db"
    sqlite_url = f"sqlite:///{db_path.as_posix()}"
    eng = create_engine(sqlite_url, connect_args={"check_same_thread": False}, future=True)
    SessionLocal_local = sessionmaker(
        bind=eng, autoflush=False, autocommit=False, expire_on_commit=False, future=True
    )
    logger.info("Using local SQLite database: %s", db_path)
    return eng, SessionLocal_local, "local-sqlite"


engine, SessionLocal, _active_db_label = _resolve_engine()


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Safe to call on startup."""
    from backend.models import test_generation  # noqa: F401

    Base.metadata.create_all(bind=engine)


def active_db_label() -> str:
    """Return a human-readable label for the current database backend."""
    return _active_db_label
