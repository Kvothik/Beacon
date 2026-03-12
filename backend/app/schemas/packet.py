from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PacketCreateRequest(BaseModel):
    offender_sid: str
    offender_name: str
    offender_tdcj_number: Optional[str] = None
    current_facility: Optional[str] = None
    parole_board_office_code: Optional[str] = None


class PacketCreateResponse(BaseModel):
    id: str
    status: str
    offender_sid: str
    offender_name: str
    offender_tdcj_number: Optional[str] = None
    current_facility: Optional[str] = None
    parole_board_office_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime
