from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=64)
    email: str
    password: str = Field(..., min_length=6, max_length=128)
    gender: str = "unspecified"

class AuthResponse(BaseModel):
    token: str
    user: dict

class UserProfile(BaseModel):
    id: str
    nickname: str
    email: str
    gender: str
    avatar: Optional[str] = None
    level: int
    xp: int
    is_premium: bool
    membership_plan: str
    preferences: Optional[dict] = None
    created_at: Optional[datetime] = None

class PreferencesUpdate(BaseModel):
    preferences: dict = Field(default_factory=dict)

class ApiResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Optional[dict] = None

class MessageResponse(BaseModel):
    message: str
