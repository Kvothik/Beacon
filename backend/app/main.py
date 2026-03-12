from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.core.config import settings
from backend.app.core.db import get_database_state, initialize_database, shutdown_database
from backend.app.routers.auth_router import router as auth_router
from backend.app.routers.offender_router import router as offender_router
from backend.app.routers.packet_router import router as packet_router
from backend.app.routers.parole_board_router import router as parole_board_router
from backend.app.routers.pdf_router import router as pdf_router
from backend.app.routers.upload_router import router as upload_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    try:
        yield
    finally:
        shutdown_database()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, object]:
    db_state = get_database_state()
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "database": {
            "configured": bool(db_state.url),
            "connected": db_state.connected,
        },
    }


app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(offender_router, prefix=settings.api_v1_prefix)
app.include_router(parole_board_router, prefix=settings.api_v1_prefix)
app.include_router(packet_router, prefix=settings.api_v1_prefix)
app.include_router(upload_router, prefix=settings.api_v1_prefix)
app.include_router(pdf_router, prefix=settings.api_v1_prefix)
