from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.membership import Membership, SubscriptionPlan

LEVEL_HIERARCHY = {
    "free": 0,
    "basic": 1,
    "premium": 2,
}


async def get_user_membership_level(user_id: str) -> str:
    """Return the membership level string for a user ('free', 'basic', 'premium')."""
    async with async_session_factory() as db:
        result = await db.execute(
            select(Membership)
            .where(Membership.user_id == user_id)
            .where(Membership.status == "active")
        )
        membership = result.scalar_one_or_none()
        if not membership or not membership.plan_id:
            return "free"

        plan_result = await db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == membership.plan_id)
        )
        plan = plan_result.scalar_one_or_none()
        if not plan:
            return "free"

        return plan.level


async def check_premium_access(user_id: str, required_level: str = "basic") -> bool:
    """Check if user has active membership of required_level or higher.

    Args:
        user_id: The user's ID
        required_level: One of 'free', 'basic', 'premium'. Default is 'basic'.

    Returns:
        True if user has sufficient membership level, False otherwise.
    """
    user_level = await get_user_membership_level(user_id)
    required = LEVEL_HIERARCHY.get(required_level, 0)
    current = LEVEL_HIERARCHY.get(user_level, 0)
    return current >= required
