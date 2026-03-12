from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from backend.app.core.security import ApiError, require_authenticated_user
from backend.app.services.parole_board_service import lookup_parole_board_office

router = APIRouter(prefix="/parole-board-office", tags=["parole-board"], dependencies=[Depends(require_authenticated_user)])


class ParoleBoardOfficeResponse(BaseModel):
    office_code: str
    office_name: str
    address_lines: list[str]
    city: str
    state: str
    postal_code: str
    phone: Optional[str] = None
    notes: Optional[str] = None


@router.get("", response_model=ParoleBoardOfficeResponse)
def get_parole_board_office(unit: str = Query(...), sid: Optional[str] = Query(None)) -> ParoleBoardOfficeResponse:
    normalized_unit = unit.strip()
    if not normalized_unit:
        raise ApiError(
            400,
            "validation_error",
            "Request validation failed.",
            details={"fields": ["unit"]},
        )

    office = lookup_parole_board_office(normalized_unit, sid=sid)
    return ParoleBoardOfficeResponse(**office)
