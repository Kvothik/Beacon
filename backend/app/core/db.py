from __future__ import annotations

from dataclasses import dataclass
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import settings


@dataclass
class DatabaseState:
    url: str
    connected: bool = False


_db_state = DatabaseState(url=settings.database_url)
_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def initialize_database() -> None:
    """Initialize the SQLAlchemy engine and attempt a lightweight connectivity check."""
    global _engine, _session_factory

    if _engine is None:
        _engine = create_engine(settings.database_url, future=True)
        _session_factory = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)

    try:
        with _engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        _db_state.connected = True
    except SQLAlchemyError:
        _db_state.connected = False


def shutdown_database() -> None:
    global _engine, _session_factory

    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None
    _db_state.connected = False


def get_database_state() -> DatabaseState:
    return _db_state


def get_engine() -> Engine:
    if _engine is None:
        initialize_database()
    if _engine is None:
        raise RuntimeError("Database engine is not initialized")
    return _engine


def create_session() -> Session:
    if _session_factory is None:
        initialize_database()
    if _session_factory is None:
        raise RuntimeError("Database session factory is not initialized")
    return _session_factory()


def get_session() -> Generator[Session, None, None]:
    session = create_session()
    try:
        yield session
    finally:
        session.close()
