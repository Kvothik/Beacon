from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

PLATFORM_VALUES = ("ios", "android")


class NotificationSubscription(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notification_subscriptions"
    __table_args__ = (
        CheckConstraint(f"platform IN {PLATFORM_VALUES}", name="ck_notification_subscriptions_platform_allowed"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    platform: Mapped[str] = mapped_column(Text, nullable=False)
    device_token: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    user = relationship("User", back_populates="notification_subscriptions")
