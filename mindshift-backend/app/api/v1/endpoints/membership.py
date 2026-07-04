from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.membership import Membership, PaymentRecord, SubscriptionPlan
from app.models.user import User
from app.schemas.membership import (
    MembershipCancelResponse,
    MembershipRestoreResponse,
    MembershipUpgradeRequest,
    MembershipUpgradeResponse,
    MembershipVerifyReceiptRequest,
)

router = APIRouter(prefix="/membership", tags=["membership"])


@router.get("/plans")
async def list_plans(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(SubscriptionPlan).order_by(SubscriptionPlan.sort_order)
    )
    plans = result.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "level": p.level,
            "price_monthly": p.price_monthly,
            "price_quarterly": p.price_quarterly,
            "price_annually": p.price_annually,
            "features": p.features,
            "sort_order": p.sort_order,
        }
        for p in plans
    ]


@router.get("/status")
async def membership_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Membership).where(Membership.user_id == current_user.id)
    )
    membership = result.scalar_one_or_none()

    if not membership:
        return {
            "has_membership": False,
            "plan_name": "Free",
            "status": "active",
            "expires_at": None,
        }

    plan_name = "Free"
    if membership.plan_id:
        plan_result = await db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == membership.plan_id)
        )
        plan = plan_result.scalar_one_or_none()
        if plan:
            plan_name = plan.name

    return {
        "has_membership": True,
        "plan_name": plan_name,
        "status": membership.status,
        "starts_at": membership.starts_at.isoformat(),
        "expires_at": membership.expires_at.isoformat() if membership.expires_at else None,
        "auto_renew": membership.auto_renew,
    }


@router.post("/upgrade", response_model=MembershipUpgradeResponse)
async def upgrade_membership(
    data: MembershipUpgradeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan_result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == data.plan_id)
    )
    plan = plan_result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.level == "free":
        raise HTTPException(status_code=400, detail="Cannot upgrade to free plan")

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=30)  # Default 1 month

    existing_result = await db.execute(
        select(Membership).where(Membership.user_id == current_user.id)
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        existing.plan_id = plan.id
        existing.status = "active"
        existing.starts_at = now
        existing.expires_at = expires_at
        existing.auto_renew = True
        membership = existing
    else:
        membership = Membership(
            user_id=current_user.id,
            plan_id=plan.id,
            status="active",
            starts_at=now,
            expires_at=expires_at,
            auto_renew=True,
        )
        db.add(membership)

    payment = PaymentRecord(
        user_id=current_user.id,
        plan_id=plan.id,
        amount=plan.price_monthly or 0,
        currency="CNY",
        status="completed",
    )
    db.add(payment)

    await db.flush()

    return {
        "success": True,
        "membership_id": membership.id,
        "plan_name": plan.name,
        "status": "active",
        "starts_at": membership.starts_at.isoformat(),
        "expires_at": membership.expires_at.isoformat() if membership.expires_at else None,
    }


@router.post("/cancel", response_model=MembershipCancelResponse)
async def cancel_membership(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Membership).where(
            and_(
                Membership.user_id == current_user.id,
                Membership.status == "active",
            )
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="No active membership found")

    now = datetime.now(timezone.utc)
    membership.auto_renew = False
    membership.status = "cancelled"
    await db.flush()

    return {
        "success": True,
        "message": "Membership cancelled successfully",
        "cancelled_at": now.isoformat(),
    }


@router.post("/restore", response_model=MembershipRestoreResponse)
async def restore_membership(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Membership)
        .where(Membership.user_id == current_user.id)
        .order_by(Membership.starts_at.desc())
        .limit(1)
    )
    membership = result.scalar_one_or_none()

    if not membership:
        return {
            "found": False,
            "plan_name": "Free",
            "level": "free",
            "status": "active",
            "expires_at": None,
            "auto_renew": False,
        }

    plan_name = "Free"
    plan_level = "free"
    if membership.plan_id:
        plan_result = await db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == membership.plan_id)
        )
        plan = plan_result.scalar_one_or_none()
        if plan:
            plan_name = plan.name
            plan_level = plan.level

    # If membership is still active or valid, restore it
    if membership.status == "cancelled":
        membership.status = "active"
        membership.auto_renew = True
        await db.flush()

    return {
        "found": True,
        "plan_name": plan_name,
        "level": plan_level,
        "status": membership.status,
        "expires_at": membership.expires_at.isoformat() if membership.expires_at else None,
        "auto_renew": membership.auto_renew,
    }


@router.post("/verify-receipt")
async def verify_receipt(
    data: MembershipVerifyReceiptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # For development: store the receipt and mark as verified
    # In production, this would verify with Apple's receipt validation server
    now = datetime.now(timezone.utc)

    payment = PaymentRecord(
        user_id=current_user.id,
        amount=0,
        currency="CNY",
        receipt_data=data.receipt_data,
        transaction_id=data.transaction_id,
        status="verified",
        created_at=now,
    )
    db.add(payment)
    await db.flush()

    # Activate the user's membership
    existing_result = await db.execute(
        select(Membership).where(Membership.user_id == current_user.id)
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        existing.status = "active"
        existing.auto_renew = True
        existing.starts_at = now
        existing.expires_at = now + timedelta(days=30)
    else:
        membership = Membership(
            user_id=current_user.id,
            status="active",
            starts_at=now,
            expires_at=now + timedelta(days=30),
            auto_renew=True,
        )
        db.add(membership)

    await db.flush()

    return {
        "verified": True,
        "transaction_id": data.transaction_id,
        "status": "active",
        "expires_at": (now + timedelta(days=30)).isoformat(),
    }
