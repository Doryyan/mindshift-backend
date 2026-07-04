from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RpScenario(Base):
    __tablename__ = "rp_scenarios"

    id: Mapped[str] = mapped_column(String(10), primary_key=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    nlp_techniques: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    role_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    opening_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_premium: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    dialogues: Mapped[list["RpDialogueSession"]] = relationship(
        "RpDialogueSession", back_populates="scenario"
    )


class RpDialogueSession(Base):
    __tablename__ = "rp_dialogue_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    scenario_id: Mapped[str] = mapped_column(
        String(10), ForeignKey("rp_scenarios.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    messages: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    nlp_score: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="dialogues")  # noqa: F821
    scenario: Mapped["RpScenario"] = relationship("RpScenario", back_populates="dialogues")
