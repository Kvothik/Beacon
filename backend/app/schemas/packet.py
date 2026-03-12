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


class PacketOffenderResponse(BaseModel):
    sid: str
    name: str
    tdcj_number: Optional[str] = None
    current_facility: Optional[str] = None


class PacketSectionResponse(BaseModel):
    section_key: str
    title: str
    is_populated: bool
    notes_text: Optional[str] = None
    document_count: int


class PacketDetailResponse(BaseModel):
    id: str
    status: str
    offender: PacketOffenderResponse
    parole_board_office_code: Optional[str] = None
    sections: list[PacketSectionResponse]
    created_at: datetime
    updated_at: datetime
