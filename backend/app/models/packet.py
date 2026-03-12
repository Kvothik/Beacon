from __future__ import annotations

import uuid
from typing import Optional

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

PACKET_STATUS_VALUES = ("draft", "generating_pdf", "ready")
SECTION_KEY_VALUES = (
    "photos",
    "support_letters",
    "reflection_letter",
    "certificates_and_education",
    "future_employment",
    "parole_plan",
    "court_and_case_documents",
    "other_miscellaneous",
)


class Packet(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "packets"
    __table_args__ = (
        CheckConstraint(
            f"status IN {PACKET_STATUS_VALUES}",
            name="ck_packets_status_allowed",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    offender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("offenders.id"), nullable=False)
    parole_board_office_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("parole_board_offices.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    sender_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sender_phone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sender_email: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sender_relationship: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cover_letter_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    final_pdf_storage_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    final_pdf_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="packets")
    offender = relationship("Offender", back_populates="packets")
    parole_board_office = relationship("ParoleBoardOffice", back_populates="packets")
    sections = relationship("PacketSection", back_populates="packet")


class PacketSection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "packet_sections"
    __table_args__ = (
        UniqueConstraint("packet_id", "section_key", name="uq_packet_sections_packet_section_key"),
        CheckConstraint(
            f"section_key IN {SECTION_KEY_VALUES}",
            name="ck_packet_sections_section_key_allowed",
        ),
    )

    packet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packets.id"), nullable=False)
    section_key: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    notes_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_populated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    packet = relationship("Packet", back_populates="sections")
    documents = relationship("Document", back_populates="packet_section")
