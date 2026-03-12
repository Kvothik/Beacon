from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import ApiError
from backend.app.models.offender import Offender
from backend.app.models.packet import Packet, PacketSection
from backend.app.models.parole_board import ParoleBoardOffice
from backend.app.models.user import User

PACKET_SECTION_DEFINITIONS: list[dict[str, Any]] = [
    {"section_key": "photos", "title": "Photos", "sort_order": 1},
    {"section_key": "support_letters", "title": "Support Letters", "sort_order": 2},
    {"section_key": "reflection_letter", "title": "Reflection Letter", "sort_order": 3},
    {"section_key": "certificates_and_education", "title": "Certificates and Education", "sort_order": 4},
    {"section_key": "future_employment", "title": "Future Employment", "sort_order": 5},
    {"section_key": "parole_plan", "title": "Parole Plan", "sort_order": 6},
    {"section_key": "court_and_case_documents", "title": "Court and Case Documents", "sort_order": 7},
    {"section_key": "other_miscellaneous", "title": "Other or Miscellaneous", "sort_order": 8},
]


def create_packet(
    session: Session,
    *,
    current_user: User,
    offender_sid: str,
    offender_name: str,
    offender_tdcj_number: str | None,
    current_facility: str | None,
    parole_board_office_code: str | None,
) -> dict[str, Any]:
    normalized_sid = offender_sid.strip()
    normalized_name = offender_name.strip()
    if not normalized_sid or not normalized_name:
        raise ApiError(
            400,
            "validation_error",
            "Request validation failed.",
            details={"fields": [field for field, value in (("offender_sid", normalized_sid), ("offender_name", normalized_name)) if not value]},
        )

    parole_board_office = None
    normalized_office_code = parole_board_office_code.strip() if parole_board_office_code else None
    if normalized_office_code:
        parole_board_office = session.scalar(
            select(ParoleBoardOffice).where(ParoleBoardOffice.office_code == normalized_office_code)
        )
        if parole_board_office is None:
            raise ApiError(
                404,
                "not_found",
                "No parole board office was found for that office code.",
                details={"parole_board_office_code": normalized_office_code},
            )

    offender = Offender(
        sid=normalized_sid,
        name=normalized_name,
        tdcj_number=offender_tdcj_number.strip() if offender_tdcj_number else None,
        current_facility=current_facility.strip() if current_facility else None,
        retrieved_at=datetime.now(timezone.utc),
    )
    session.add(offender)
    session.flush()

    packet = Packet(
        user_id=current_user.id,
        offender_id=offender.id,
        parole_board_office_id=parole_board_office.id if parole_board_office else None,
        status="draft",
    )
    session.add(packet)
    session.flush()

    for section_definition in PACKET_SECTION_DEFINITIONS:
        session.add(
            PacketSection(
                packet_id=packet.id,
                section_key=section_definition["section_key"],
                title=section_definition["title"],
                sort_order=section_definition["sort_order"],
                is_populated=False,
            )
        )

    session.commit()
    session.refresh(packet)
    return {
        "id": str(packet.id),
        "status": packet.status,
        "offender_sid": offender.sid,
        "offender_name": offender.name,
        "offender_tdcj_number": offender.tdcj_number,
        "current_facility": offender.current_facility,
        "parole_board_office_code": parole_board_office.office_code if parole_board_office else None,
        "created_at": packet.created_at,
        "updated_at": packet.updated_at,
    }
