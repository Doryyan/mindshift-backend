import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, Boolean, DateTime, Integer, Text, Float, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nickname: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[str] = mapped_column(String(16), default="unspecified")
    avatar: Mapped[str] = mapped_column(String(512), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=1)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    preferences: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Membership
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    membership_plan: Mapped[str] = mapped_column(String(32), default="free")
    membership_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Auth
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(String(36), nullable=True)
    lesson_id: Mapped[str] = mapped_column(String(36), nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    progress_pct: Mapped[float] = mapped_column(Float, default=0.0)
    score: Mapped[int] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
