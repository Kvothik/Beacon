from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.security import ApiError
from backend.app.models.document import DOCUMENT_SOURCE_VALUES, Document
from backend.app.models.offender import Offender
from backend.app.models.packet import SECTION_KEY_VALUES, Packet, PacketSection
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
UPLOAD_URL_PLACEHOLDER = "https://object-storage.example/upload"


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


def get_packet_detail(session: Session, *, current_user: User, packet_id: UUID) -> dict[str, Any]:
    packet = session.get(Packet, packet_id)
    if packet is None:
        raise ApiError(404, "packet_not_found", "No packet was found for that id.")
    if packet.user_id != current_user.id:
        raise ApiError(403, "forbidden", "You do not have access to that packet.")

    offender = session.get(Offender, packet.offender_id)
    if offender is None:
        raise ApiError(500, "internal_error", "Packet offender snapshot is missing.")

    parole_board_office_code = None
    if packet.parole_board_office_id:
        office = session.get(ParoleBoardOffice, packet.parole_board_office_id)
        parole_board_office_code = office.office_code if office else None

    sections = session.scalars(
        select(PacketSection).where(PacketSection.packet_id == packet.id).order_by(PacketSection.sort_order)
    ).all()
    document_counts = _document_counts_by_section(session, packet.id)

    return {
        "id": str(packet.id),
        "status": packet.status,
        "offender": {
            "sid": offender.sid,
            "name": offender.name,
            "tdcj_number": offender.tdcj_number,
            "current_facility": offender.current_facility,
        },
        "parole_board_office_code": parole_board_office_code,
        "sections": [
            {
                "section_key": section.section_key,
                "title": section.title,
                "is_populated": section.is_populated,
                "notes_text": section.notes_text,
                "document_count": int(document_counts.get(section.id, 0)),
            }
            for section in sections
        ],
        "created_at": packet.created_at,
        "updated_at": packet.updated_at,
    }


def update_packet_section(
    session: Session,
    *,
    current_user: User,
    packet_id: UUID,
    section_key: str,
    notes_text: str | None,
    is_populated: bool,
) -> dict[str, Any]:
    if section_key not in SECTION_KEY_VALUES:
        raise ApiError(
            400,
            "validation_error",
            "Request validation failed.",
            details={"fields": ["section_key"]},
        )

    packet = session.get(Packet, packet_id)
    if packet is None:
        raise ApiError(404, "packet_not_found", "No packet was found for that id.")
    if packet.user_id != current_user.id:
        raise ApiError(403, "forbidden", "You do not have access to that packet.")

    section = session.scalar(
        select(PacketSection).where(PacketSection.packet_id == packet.id, PacketSection.section_key == section_key)
    )
    if section is None:
        raise ApiError(404, "not_found", "No packet section was found for that key.")

    section.notes_text = notes_text.strip() if notes_text is not None else None
    section.is_populated = is_populated
    session.commit()
    session.refresh(section)

    document_counts = _document_counts_by_section(session, packet.id)
    return {
        "section_key": section.section_key,
        "title": section.title,
        "notes_text": section.notes_text,
        "is_populated": section.is_populated,
        "document_count": int(document_counts.get(section.id, 0)),
        "updated_at": section.updated_at,
    }


def create_packet_upload(
    session: Session,
    *,
    current_user: User,
    packet_id: UUID,
    section_key: str,
    filename: str,
    content_type: str,
    source: str,
) -> dict[str, Any]:
    packet = session.get(Packet, packet_id)
    if packet is None:
        raise ApiError(404, "packet_not_found", "No packet was found for that id.")
    if packet.user_id != current_user.id:
        raise ApiError(403, "forbidden", "You do not have access to that packet.")
    if section_key not in SECTION_KEY_VALUES:
        raise ApiError(400, "validation_error", "Request validation failed.", details={"fields": ["section_key"]})
    if source not in DOCUMENT_SOURCE_VALUES:
        raise ApiError(400, "validation_error", "Request validation failed.", details={"fields": ["source"]})

    section = session.scalar(
        select(PacketSection).where(PacketSection.packet_id == packet.id, PacketSection.section_key == section_key)
    )
    if section is None:
        raise ApiError(404, "not_found", "No packet section was found for that key.")

    cleaned_filename = Path(filename.strip()).name
    if not cleaned_filename or not content_type.strip():
        raise ApiError(
            400,
            "validation_error",
            "Request validation failed.",
            details={"fields": [field for field, value in (("filename", cleaned_filename), ("content_type", content_type.strip())) if not value]},
        )

    document = Document(
        packet_id=packet.id,
        packet_section_id=section.id,
        filename=cleaned_filename,
        content_type=content_type.strip(),
        source=source,
        upload_status="pending",
    )
    session.add(document)
    session.flush()

    storage_key = f"packets/{packet.id}/documents/{document.id}-{cleaned_filename}"
    document.storage_key = storage_key
    session.commit()
    session.refresh(document)

    return {
        "document_id": str(document.id),
        "packet_id": str(packet.id),
        "section_key": section.section_key,
        "filename": document.filename,
        "content_type": document.content_type,
        "upload_status": document.upload_status,
        "upload_url": UPLOAD_URL_PLACEHOLDER,
        "storage_key": storage_key,
        "created_at": document.created_at,
    }


def _document_counts_by_section(session: Session, packet_id: UUID) -> dict[UUID, int]:
    return {
        section_id: count
        for section_id, count in session.execute(
            select(Document.packet_section_id, func.count(Document.id))
            .where(Document.packet_id == packet_id)
            .group_by(Document.packet_section_id)
        ).all()
    }
