from __future__ import annotations

from dataclasses import dataclass

from backend.app.core.config import settings


@dataclass
class DatabaseState:
    url: str
    connected: bool = False


_db_state = DatabaseState(url=settings.database_url)


def initialize_database() -> None:
    """Initialize backend database state for application startup.

    Issue #2 only requires runtime wiring, not a real database connection.
    """
    _db_state.connected = True


def shutdown_database() -> None:
    _db_state.connected = False


def get_database_state() -> DatabaseState:
    return _db_state
