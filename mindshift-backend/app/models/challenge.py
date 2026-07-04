from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class WeeklyChallenge(Base):
    __tablename__ = "weekly_challenges"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # skill/scenario/community/streak
    requirement: Mapped[dict] = mapped_column(JSON, nullable=False)
    reward_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ends_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user_challenges: Mapped[list["UserChallenge"]] = relationship(
        "UserChallenge", back_populates="challenge"
    )


class UserChallenge(Base):
    __tablename__ = "user_challenges"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    challenge_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("weekly_challenges.id", ondelete="CASCADE"), nullable=False
    )
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0-100
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="user_challenges")  # noqa: F821
    challenge: Mapped["WeeklyChallenge"] = relationship(
        "WeeklyChallenge", back_populates="user_challenges"
    )
