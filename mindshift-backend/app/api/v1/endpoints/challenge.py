from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.challenge import UserChallenge, WeeklyChallenge
from app.models.membership import NlpSkillProfile
from app.models.user import User

router = APIRouter(prefix="/challenges", tags=["challenges"])


@router.get("/current")
async def get_current_challenge(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(WeeklyChallenge)
        .where(
            WeeklyChallenge.is_active == True,
            WeeklyChallenge.starts_at <= now,
            WeeklyChallenge.ends_at >= now,
        )
        .order_by(WeeklyChallenge.starts_at.desc())
        .limit(1)
    )
    challenge = result.scalar_one_or_none()
    if not challenge:
        return {"challenge": None}

    # Get user's progress for this challenge
    result = await db.execute(
        select(UserChallenge).where(
            UserChallenge.user_id == current_user.id,
            UserChallenge.challenge_id == challenge.id,
        )
    )
    user_challenge = result.scalar_one_or_none()

    return {
        "challenge": {
            "id": challenge.id,
            "title": challenge.title,
            "description": challenge.description,
            "type": challenge.type,
            "requirement": challenge.requirement,
            "reward_xp": challenge.reward_xp,
            "starts_at": challenge.starts_at.isoformat(),
            "ends_at": challenge.ends_at.isoformat(),
        },
        "user_progress": {
            "progress": user_challenge.progress if user_challenge else 0,
            "completed_at": user_challenge.completed_at.isoformat()
            if user_challenge and user_challenge.completed_at
            else None,
        },
    }


@router.get("/user/{user_id}")
async def get_user_challenges(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserChallenge, WeeklyChallenge)
        .join(WeeklyChallenge, UserChallenge.challenge_id == WeeklyChallenge.id)
        .where(UserChallenge.user_id == user_id)
        .order_by(WeeklyChallenge.starts_at.desc())
    )
    rows = result.all()
    return {
        "challenges": [
            {
                "id": uc.id,
                "challenge_id": wc.id,
                "title": wc.title,
                "type": wc.type,
                "reward_xp": wc.reward_xp,
                "progress": uc.progress,
                "completed_at": uc.completed_at.isoformat()
                if uc.completed_at
                else None,
                "created_at": uc.created_at.isoformat(),
            }
            for uc, wc in rows
        ]
    }


@router.post("/complete")
async def complete_challenge(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)

    # Find current active challenge
    result = await db.execute(
        select(WeeklyChallenge)
        .where(
            WeeklyChallenge.is_active == True,
            WeeklyChallenge.starts_at <= now,
            WeeklyChallenge.ends_at >= now,
        )
        .limit(1)
    )
    challenge = result.scalar_one_or_none()
    if not challenge:
        raise HTTPException(status_code=404, detail="No active challenge found")

    # Find or create user challenge
    result = await db.execute(
        select(UserChallenge).where(
            UserChallenge.user_id == current_user.id,
            UserChallenge.challenge_id == challenge.id,
        )
    )
    user_challenge = result.scalar_one_or_none()

    if not user_challenge:
        user_challenge = UserChallenge(
            user_id=current_user.id,
            challenge_id=challenge.id,
            progress=100,
            completed_at=now,
        )
        db.add(user_challenge)
    else:
        if user_challenge.completed_at:
            raise HTTPException(
                status_code=400, detail="Challenge already completed"
            )
        user_challenge.progress = 100
        user_challenge.completed_at = now

    # Award XP by updating the skill profile
    result = await db.execute(
        select(NlpSkillProfile).where(
            NlpSkillProfile.user_id == current_user.id
        )
    )
    profile = result.scalar_one_or_none()
    if profile:
        profile.total_trainings += challenge.reward_xp

    await db.flush()

    return {
        "challenge_id": challenge.id,
        "reward_xp": challenge.reward_xp,
        "completed_at": now.isoformat(),
        "message": f"完成挑战！获得 {challenge.reward_xp} XP",
    }
