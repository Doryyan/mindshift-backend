from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ScenarioListItem(BaseModel):
    id: str
    category: str
    title: str
    description: str | None = None
    difficulty: str
    is_premium: bool

    model_config = {"from_attributes": True}


class ScenarioDetail(BaseModel):
    id: str
    category: str
    title: str
    description: str | None = None
    difficulty: str
    nlp_techniques: dict | None = None
    role_prompt: str | None = None
    opening_message: str | None = None
    is_premium: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DialogueStartRequest(BaseModel):
    scenario_id: str


class DialogueChatRequest(BaseModel):
    message: str


class DialogueMessageResponse(BaseModel):
    role: str
    content: str
    timestamp: str | None = None


class DialogueSessionResponse(BaseModel):
    id: str
    scenario_id: str
    status: str
    messages: list = []
    nlp_score: dict | None = None
    started_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class DialogueHistoryResponse(BaseModel):
    id: str
    scenario_id: str
    status: str
    messages: list = []
    nlp_score: dict | None = None
    started_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}
