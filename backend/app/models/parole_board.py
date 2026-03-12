from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ParoleBoardOffice(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "parole_board_offices"

    office_code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    office_name: Mapped[str] = mapped_column(Text, nullable=False)
    address_line_1: Mapped[str] = mapped_column(Text, nullable=False)
    address_line_2: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[str] = mapped_column(Text, nullable=False)
    postal_code: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    packets = relationship("Packet", back_populates="parole_board_office")
    unit_mappings = relationship("ParoleBoardUnitMapping", back_populates="office")


class ParoleBoardUnitMapping(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "parole_board_unit_mappings"

    unit_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    office_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("parole_board_offices.id"), nullable=False)

    office = relationship("ParoleBoardOffice", back_populates="unit_mappings")
