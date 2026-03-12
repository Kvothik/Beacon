from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Offender(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "offenders"
    __table_args__ = (
        UniqueConstraint("sid", "retrieved_at", name="uq_offenders_sid_retrieved_at"),
        Index("ix_offenders_sid", "sid"),
    )

    sid: Mapped[str] = mapped_column(Text, nullable=False)
    tdcj_number: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    race: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_facility: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    projected_release_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parole_eligibility_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    maximum_sentence_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    visitation_eligible: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    visitation_eligible_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(Text, nullable=False, default="Texas Department of Criminal Justice")
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    packets = relationship("Packet", back_populates="offender")
