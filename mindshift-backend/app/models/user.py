from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str] = mapped_column(
        Enum("male", "female", "unspecified", name="gender_enum"),
        default="unspecified",
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    stage: Mapped[str] = mapped_column(
        Enum("beginner", "intermediate", "advanced", name="stage_enum"),
        default="beginner",
        nullable=False,
    )
    preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    skill_profile: Mapped["NlpSkillProfile | None"] = relationship(
        "NlpSkillProfile", back_populates="user", uselist=False
    )
    training_records: Mapped[list["NlpTrainingRecord"]] = relationship(
        "NlpTrainingRecord", back_populates="user"
    )
    dialogues: Mapped[list["RpDialogueSession"]] = relationship(
        "RpDialogueSession", back_populates="user"
    )
    posts: Mapped[list["CommunityPost"]] = relationship("CommunityPost", back_populates="user")
    comments: Mapped[list["PostComment"]] = relationship("PostComment", back_populates="user")
    checkins: Mapped[list["Checkin"]] = relationship("Checkin", back_populates="user")
    membership: Mapped["Membership | None"] = relationship(
        "Membership", back_populates="user", uselist=False
    )
    user_challenges: Mapped[list["UserChallenge"]] = relationship(
        "UserChallenge", back_populates="user"
    )
    growth_stories: Mapped[list["GrowthStory"]] = relationship(
        "GrowthStory", back_populates="user"
    )
    story_likes: Mapped[list["StoryLike"]] = relationship(
        "StoryLike", back_populates="user"
    )
    expert_questions: Mapped[list["ExpertQuestion"]] = relationship(
        "ExpertQuestion", back_populates="user"
    )
