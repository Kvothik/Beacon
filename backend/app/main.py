from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.db import get_database_state, initialize_database, shutdown_database
from backend.app.core.security import ApiError
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


@app.exception_handler(ApiError)
async def handle_api_error(_request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "retryable": exc.retryable,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
    fields = sorted({".".join(str(part) for part in error["loc"][1:]) for error in exc.errors()})
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed.",
                "details": {"fields": fields},
                "retryable": False,
            }
        },
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
