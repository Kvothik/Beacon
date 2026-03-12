from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

DOCUMENT_SOURCE_VALUES = ("scanner", "upload")
UPLOAD_STATUS_VALUES = ("pending", "uploaded", "failed")


class Document(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint(f"source IN {DOCUMENT_SOURCE_VALUES}", name="ck_documents_source_allowed"),
        CheckConstraint(
            f"upload_status IN {UPLOAD_STATUS_VALUES}",
            name="ck_documents_upload_status_allowed",
        ),
    )

    packet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packets.id"), nullable=False)
    packet_section_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packet_sections.id"), nullable=False)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    storage_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    upload_status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    packet_section = relationship("PacketSection", back_populates="documents")
