from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str


class UserRegister(BaseModel):
    email: str
    password: str = Field(min_length=6, max_length=100)
    nickname: str = Field(min_length=1, max_length=100)
    gender: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    nickname: str
    gender: str
    avatar_url: str | None = None
    stage: str
    preferences: dict | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RefreshToken(BaseModel):
    token: str


class PreferencesUpdate(BaseModel):
    preferences: dict
