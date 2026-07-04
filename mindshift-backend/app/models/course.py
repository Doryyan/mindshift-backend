from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class NlpCourse(Base):
    __tablename__ = "nlp_courses"

    id: Mapped[str] = mapped_column(String(10), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lesson_count: Mapped[int] = mapped_column(default=0, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(default=0, nullable=False)
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    cover_emoji: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_premium: Mapped[bool] = mapped_column(default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    lessons: Mapped[list["NlpLesson"]] = relationship(
        "NlpLesson", back_populates="course", order_by="NlpLesson.order_num"
    )


class NlpLesson(Base):
    __tablename__ = "nlp_lessons"

    id: Mapped[str] = mapped_column(String(10), primary_key=True)
    course_id: Mapped[str] = mapped_column(
        String(10), ForeignKey("nlp_courses.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    concepts: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source_refs: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    order_num: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    course: Mapped["NlpCourse"] = relationship("NlpCourse", back_populates="lessons")
