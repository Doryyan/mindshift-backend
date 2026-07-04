from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class NlpSkillProfile(Base):
    __tablename__ = "nlp_skill_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    sensory_acuity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rapport_building: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    belief_transformation: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    submodality_mastery: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    language_pattern: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    state_management: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    anchoring_skill: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reframing_skill: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_trainings: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_roleplays: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship("User", back_populates="skill_profile")  # noqa: F821


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)  # free/basic/premium
    price_monthly: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_quarterly: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_annually: Mapped[float | None] = mapped_column(Float, nullable=True)
    features: Mapped[dict] = mapped_column(JSON, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    memberships: Mapped[list["Membership"]] = relationship("Membership", back_populates="plan")


class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("subscription_plans.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="active", nullable=False
    )  # active/expired/cancelled
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    auto_renew: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="membership")  # noqa: F821
    plan: Mapped["SubscriptionPlan | None"] = relationship(
        "SubscriptionPlan", back_populates="memberships"
    )


class PaymentRecord(Base):
    __tablename__ = "payment_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("subscription_plans.id", ondelete="SET NULL"), nullable=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="CNY", nullable=False)
    receipt_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    transaction_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
