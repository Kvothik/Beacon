from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("BEACON_APP_NAME", "Beacon API")
    api_v1_prefix: str = os.getenv("BEACON_API_V1_PREFIX", "/api/v1")
    environment: str = os.getenv("BEACON_ENV", "development")
    debug: bool = os.getenv("BEACON_DEBUG", "false").lower() == "true"
    database_url: str = os.getenv("BEACON_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/beacon")


settings = Settings()
