from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.db import get_session
from backend.app.core.security import require_authenticated_user
from backend.app.models.user import User
from backend.app.schemas.packet import (
    PacketCreateRequest,
    PacketCreateResponse,
    PacketDetailResponse,
    PacketSectionUpdateRequest,
    PacketSectionUpdateResponse,
)
from backend.app.services.packet_service import create_packet, get_packet_detail, update_packet_section

router = APIRouter(prefix="/packets", tags=["packets"], dependencies=[Depends(require_authenticated_user)])


@router.post("", response_model=PacketCreateResponse, status_code=status.HTTP_201_CREATED)
def create_packet_draft(
    payload: PacketCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_authenticated_user),
) -> PacketCreateResponse:
    packet = create_packet(
        session,
        current_user=current_user,
        offender_sid=payload.offender_sid,
        offender_name=payload.offender_name,
        offender_tdcj_number=payload.offender_tdcj_number,
        current_facility=payload.current_facility,
        parole_board_office_code=payload.parole_board_office_code,
    )
    return PacketCreateResponse(**packet)


@router.get("/{packet_id}", response_model=PacketDetailResponse)
def read_packet_detail(
    packet_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_authenticated_user),
) -> PacketDetailResponse:
    packet = get_packet_detail(session, current_user=current_user, packet_id=packet_id)
    return PacketDetailResponse(**packet)


@router.patch("/{packet_id}/sections/{section_key}", response_model=PacketSectionUpdateResponse)
def update_packet_section_detail(
    packet_id: UUID,
    section_key: str,
    payload: PacketSectionUpdateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_authenticated_user),
) -> PacketSectionUpdateResponse:
    section = update_packet_section(
        session,
        current_user=current_user,
        packet_id=packet_id,
        section_key=section_key,
        notes_text=payload.notes_text,
        is_populated=payload.is_populated,
    )
    return PacketSectionUpdateResponse(**section)
