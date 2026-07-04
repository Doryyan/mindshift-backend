from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class PostCreate(BaseModel):
    content: str
    topic_tags: list[str] | None = None


class PostListItem(BaseModel):
    id: str
    user_id: str
    content: str
    topic_tags: list | None = None
    likes_count: int
    comments_count: int
    is_pinned: bool
    created_at: datetime
    user_nickname: str | None = None
    user_avatar: str | None = None

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    content: str
    parent_id: str | None = None


class CommentResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    content: str
    parent_id: str | None = None
    created_at: datetime
    user_nickname: str | None = None

    model_config = {"from_attributes": True}


class PostDetail(BaseModel):
    id: str
    user_id: str
    content: str
    topic_tags: list | None = None
    likes_count: int
    comments_count: int
    is_pinned: bool
    created_at: datetime
    user_nickname: str | None = None
    user_avatar: str | None = None
    comments: list[CommentResponse] = []

    model_config = {"from_attributes": True}


class CheckinRequest(BaseModel):
    mood: str | None = None
    note: str | None = None


class CheckinStatus(BaseModel):
    checked_in: bool
    streak_count: int
    today_checkin: dict | None = None
