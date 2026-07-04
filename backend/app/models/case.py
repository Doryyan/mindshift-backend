import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Boolean, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Case(Base):
    __tablename__ = "cases"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    scenario_description: Mapped[str] = mapped_column(Text, nullable=True)
    techniques_applied: Mapped[str] = mapped_column(Text, default="{}")  # JSON string for SQLite compat
    key_learning: Mapped[str] = mapped_column(Text, nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
