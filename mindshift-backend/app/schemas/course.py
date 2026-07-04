from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LessonResponse(BaseModel):
    id: str
    course_id: str
    title: str
    type: str
    content: str | None = None
    concepts: dict | None = None
    source_refs: dict | None = None
    duration: int
    order_num: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CourseListItem(BaseModel):
    id: str
    title: str
    description: str | None = None
    level: str
    lesson_count: int
    duration_minutes: int
    tags: dict | None = None
    cover_emoji: str | None = None
    is_premium: bool
    sort_order: int

    model_config = {"from_attributes": True}


class CourseDetail(BaseModel):
    id: str
    title: str
    description: str | None = None
    level: str
    source: str | None = None
    lesson_count: int
    duration_minutes: int
    tags: dict | None = None
    cover_emoji: str | None = None
    is_premium: bool
    sort_order: int
    lessons: list[LessonResponse] = []

    model_config = {"from_attributes": True}
