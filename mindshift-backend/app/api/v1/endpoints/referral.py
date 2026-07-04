from __future__ import annotations

import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.referral import ReferralCode, ReferralRecord
from app.models.user import User

router = APIRouter(prefix="/referral", tags=["referral"])

_ALPHABET = string.ascii_uppercase + string.digits


def _generate_code(length: int = 8) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))


REWARD_TIERS = {
    1: {"xp": 50, "description": "1st referral: +50 XP, 7-day premium for both"},
    3: {"xp": 100, "badge": "播种者", "description": "3rd referral: +100 XP + '播种者' badge"},
    5: {"xp": 200, "description": "5th referral: +200 XP + 1 month premium"},
    10: {"xp": 500, "badge": "传灯人", "description": "10th referral: +500 XP + '传灯人' neon badge"},
}


@router.get("/code")
async def get_referral_code(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get or generate the user's referral code."""
    result = await db.execute(
        select(ReferralCode).where(ReferralCode.user_id == current_user.id)
    )
    code = result.scalar_one_or_none()

    if code is None:
        # Generate unique code
        for _ in range(10):
            new_code = _generate_code()
            existing = await db.scalar(
                select(ReferralCode).where(ReferralCode.code == new_code)
            )
            if existing is None:
                break
        else:
            raise HTTPException(status_code=500, detail="Failed to generate unique code")

        code = ReferralCode(
            user_id=current_user.id,
            code=new_code,
        )
        db.add(code)
        await db.flush()

    return {
        "code": code.code,
        "usage_count": code.usage_count,
        "created_at": code.created_at.isoformat() if code.created_at else None,
    }


@router.post("/apply", status_code=status.HTTP_200_OK)
async def apply_referral_code(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Apply a referral code (called during or after registration)."""
    referral_code = data.get("code", "").strip().upper()
    if not referral_code:
        raise HTTPException(status_code=400, detail="Referral code is required")

    # Prevent self-referral
    result = await db.execute(
        select(ReferralCode).where(ReferralCode.code == referral_code)
    )
    ref_code = result.scalar_one_or_none()
    if not ref_code:
        raise HTTPException(status_code=404, detail="Invalid referral code")

    if ref_code.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot refer yourself")

    # Check if already referred
    existing = await db.scalar(
        select(ReferralRecord).where(
            ReferralRecord.referred_user_id == current_user.id
        )
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already applied a referral code")

    record = ReferralRecord(
        referrer_id=ref_code.user_id,
        referred_user_id=current_user.id,
    )
    ref_code.usage_count = (ref_code.usage_count or 0) + 1

    db.add(record)
    await db.flush()

    return {
        "message": "Referral code applied successfully",
        "referrer_id": ref_code.user_id,
    }


@router.get("/stats")
async def get_referral_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get referrer stats: total invites, rewards earned, tier progress."""
    total_invites = await db.scalar(
        select(func.count()).where(ReferralRecord.referrer_id == current_user.id)
    ) or 0

    # Count rewarded referrals
    rewarded_count = await db.scalar(
        select(func.count()).where(
            ReferralRecord.referrer_id == current_user.id,
            ReferralRecord.reward_granted.is_(True),
        )
    ) or 0

    # Determine current tier and next tier
    milestones = sorted(REWARD_TIERS.keys())
    current_tier = 0
    next_tier = None
    for m in milestones:
        if total_invites >= m:
            current_tier = m
        else:
            next_tier = m
            break

    tier_progress = {
        "current_tier": current_tier,
        "next_tier": next_tier,
        "total_invites": total_invites,
        "rewarded_count": rewarded_count,
        "milestones": [
            {"count": m, "xp": info["xp"], "description": info["description"]}
            for m, info in REWARD_TIERS.items()
        ],
    }

    # Total XP earned from referrals
    total_xp = 0
    for m, info in REWARD_TIERS.items():
        if total_invites >= m:
            total_xp += info["xp"]

    return {
        "total_invites": total_invites,
        "rewards_earned": rewarded_count,
        "total_xp_earned": total_xp,
        "tier_progress": tier_progress,
    }


@router.post("/claim-reward")
async def claim_referral_reward(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Claim reward for a successful referral."""
    referral_record_id = data.get("referral_record_id")
    if not referral_record_id:
        raise HTTPException(status_code=400, detail="referral_record_id is required")

    result = await db.execute(
        select(ReferralRecord).where(
            ReferralRecord.id == referral_record_id,
            ReferralRecord.referrer_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Referral record not found")
    if record.reward_granted:
        raise HTTPException(status_code=400, detail="Reward already claimed")

    record.reward_granted = True
    await db.flush()

    # Get updated stats
    total_invites = await db.scalar(
        select(func.count()).where(
            ReferralRecord.referrer_id == current_user.id,
            ReferralRecord.reward_granted.is_(True),
        )
    ) or 0

    reward_info = None
    for tier, info in sorted(REWARD_TIERS.items(), reverse=True):
        if total_invites >= tier:
            reward_info = {"tier": tier, **info}
            break

    return {
        "message": "Reward claimed successfully",
        "total_invites": total_invites,
        "reward": reward_info,
    }
