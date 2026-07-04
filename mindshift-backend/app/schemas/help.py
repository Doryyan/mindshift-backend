from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class HelpArticleListItem(BaseModel):
    id: str
    title: str
    category: str
    keywords: dict | None = None
    sort_order: int
    is_published: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class HelpArticleDetail(BaseModel):
    id: str
    title: str
    category: str
    content: str
    keywords: dict | None = None
    sort_order: int
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HelpCategoryResponse(BaseModel):
    category: str
    count: int
