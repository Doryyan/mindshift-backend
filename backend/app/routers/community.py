from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel
from app.database import get_db
from app.models.community import CommunityPost, DailyCheckin
from app.models.user import User
from app.utils.security import get_current_user, get_optional_user
from datetime import date
from typing import Optional

router = APIRouter(prefix="/api/v1/community", tags=["Community"])

class CreatePostRequest(BaseModel):
    type: str  # story/qa/training_share
    title: Optional[str] = None
    content: str
    tags: Optional[str] = None

class CheckinRequest(BaseModel):
    pass

@router.get("/posts")
async def list_posts(
    post_type: Optional[str] = Query(None, alias="type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    q = select(CommunityPost).order_by(desc(CommunityPost.is_pinned), desc(CommunityPost.created_at))
    if post_type: q = q.where(CommunityPost.type == post_type)
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    posts = result.scalars().all()
    # Count total
    count_q = select(func.count(CommunityPost.id))
    if post_type: count_q = count_q.where(CommunityPost.type == post_type)
    total = (await db.execute(count_q)).scalar()
    return {"posts": posts, "total": total, "page": page, "page_size": page_size}

@router.post("/posts")
async def create_post(
    req: CreatePostRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = CommunityPost(
        user_id=user.id, user_nickname=user.nickname,
        type=req.type, title=req.title, content=req.content, tags=req.tags
    )
    db.add(post)
    await db.flush()
    return {"success": True, "post": post}

@router.post("/checkin")
async def checkin(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today().isoformat()
    r = await db.execute(select(DailyCheckin).where(
        DailyCheckin.user_id == user.id, DailyCheckin.checkin_date == today
    ))
    if r.scalar_one_or_none():
        return {"success": True, "message": "今日已签到", "already_checked": True}
    
    # Calculate streak
    yesterday_r = await db.execute(select(DailyCheckin).where(
        DailyCheckin.user_id == user.id
    ).order_by(desc(DailyCheckin.checkin_date)).limit(1))
    last = yesterday_r.scalar_one_or_none()
    streak = (last.streak_days + 1) if last else 1
    
    checkin = DailyCheckin(user_id=user.id, checkin_date=today, streak_days=streak)
    db.add(checkin)
    # Reward XP
    user.xp += 10 + streak * 2
    await db.flush()
    return {"success": True, "streak_days": streak, "xp_earned": 10 + streak * 2}

@router.get("/checkin/status")
async def checkin_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today().isoformat()
    r = await db.execute(select(DailyCheckin).where(
        DailyCheckin.user_id == user.id, DailyCheckin.checkin_date == today
    ))
    checked = r.scalar_one_or_none()
    # Get streak
    latest_r = await db.execute(select(DailyCheckin).where(
        DailyCheckin.user_id == user.id
    ).order_by(desc(DailyCheckin.checkin_date)).limit(1))
    latest = latest_r.scalar_one_or_none()
    return {
        "checked_today": bool(checked),
        "streak_days": latest.streak_days if latest else 0,
    }
