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


class PacketSectionUpdateRequest(BaseModel):
    notes_text: Optional[str] = None
    is_populated: bool


class PacketSectionUpdateResponse(BaseModel):
    section_key: str
    title: str
    notes_text: Optional[str] = None
    is_populated: bool
    document_count: int
    updated_at: datetime


class PacketUploadCreateRequest(BaseModel):
    section_key: str
    filename: str
    content_type: str
    source: str


class PacketUploadCreateResponse(BaseModel):
    document_id: str
    packet_id: str
    section_key: str
    filename: str
    content_type: str
    upload_status: str
    upload_url: str
    storage_key: str
    created_at: datetime


class PacketCoverLetterRequest(BaseModel):
    sender_name: str
    sender_phone: str
    sender_email: str
    sender_relationship: str


class PacketCoverLetterResponse(BaseModel):
    packet_id: str
    cover_letter_text: str
    updated_at: datetime
