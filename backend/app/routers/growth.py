from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models.course import Course, Lesson, KnowledgeCard
from app.models.community import CommunityPost
from app.models.user import User
from app.utils.security import get_current_user, get_optional_user
from typing import Optional

router = APIRouter(prefix="/api/v1/growth", tags=["Growth"])

# Daily NLP Knowledge Card
@router.get("/daily-card")
async def daily_card(db: AsyncSession = Depends(get_db)):
    from datetime import date
    today = date.today().isoformat()
    r = await db.execute(select(KnowledgeCard).where(KnowledgeCard.date == today).limit(1))
    card = r.scalar_one_or_none()
    if not card:
        r = await db.execute(select(KnowledgeCard).order_by(desc(KnowledgeCard.created_at)).limit(1))
        card = r.scalar_one_or_none()
    return {"card": card}

# Growth Stories
@router.get("/stories")
async def list_stories(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    q = select(CommunityPost).where(CommunityPost.type == "story").order_by(desc(CommunityPost.created_at))
    total = (await db.execute(select(func.count(CommunityPost.id)).where(CommunityPost.type == "story"))).scalar() or 0
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    return {"stories": result.scalars().all(), "total": total, "page": page, "page_size": page_size}

@router.post("/stories")
async def create_story(req: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    post = CommunityPost(
        user_id=user.id, user_nickname=user.nickname, type="story",
        title=req.get("title", ""), content=req.get("content", ""), tags=req.get("tags", "")
    )
    db.add(post)
    await db.flush()
    return {"success": True, "post": post}

# Expert Q&A
@router.get("/qa")
async def list_qa(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    q = select(CommunityPost).where(CommunityPost.type == "qa").order_by(desc(CommunityPost.created_at))
    total = (await db.execute(select(func.count(CommunityPost.id)).where(CommunityPost.type == "qa"))).scalar() or 0
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    return {"qa_list": result.scalars().all(), "total": total, "page": page, "page_size": page_size}

@router.post("/qa")
async def create_qa(req: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    post = CommunityPost(
        user_id=user.id, user_nickname=user.nickname, type="qa",
        title=req.get("title", ""), content=req.get("content", ""), tags=req.get("tags", "")
    )
    db.add(post)
    await db.flush()
    return {"success": True, "post": post}

# Training Share
@router.get("/training-shares")
async def list_training_shares(db: AsyncSession = Depends(get_db)):
    q = select(CommunityPost).where(CommunityPost.type == "training_share").order_by(desc(CommunityPost.created_at)).limit(20)
    result = await db.execute(q)
    return result.scalars().all()
