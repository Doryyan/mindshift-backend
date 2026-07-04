from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.community import Checkin, CommunityPost, PostComment
from app.models.user import User
from app.schemas.community import (
    CheckinRequest,
    CheckinStatus,
    CommentCreate,
    CommentResponse,
    PostCreate,
    PostDetail,
    PostListItem,
)

router = APIRouter(prefix="/community", tags=["community"])


@router.post("/posts", status_code=201)
async def create_post(
    data: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = CommunityPost(
        user_id=current_user.id,
        content=data.content,
        topic_tags=data.topic_tags or [],
    )
    db.add(post)
    await db.flush()

    return {
        "id": post.id,
        "user_id": post.user_id,
        "content": post.content,
        "topic_tags": post.topic_tags,
        "likes_count": post.likes_count,
        "comments_count": post.comments_count,
        "is_pinned": post.is_pinned,
        "created_at": post.created_at.isoformat(),
        "user_nickname": current_user.nickname,
        "user_avatar": current_user.avatar_url,
    }


@router.get("/posts", response_model=list[PostListItem])
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = (
        select(CommunityPost)
        .order_by(desc(CommunityPost.is_pinned), desc(CommunityPost.created_at))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    posts = result.scalars().all()

    output = []
    for p in posts:
        user_result = await db.execute(select(User).where(User.id == p.user_id))
        post_user = user_result.scalar_one_or_none()
        output.append({
            "id": p.id,
            "user_id": p.user_id,
            "content": p.content,
            "topic_tags": p.topic_tags,
            "likes_count": p.likes_count,
            "comments_count": p.comments_count,
            "is_pinned": p.is_pinned,
            "created_at": p.created_at,
            "user_nickname": post_user.nickname if post_user else None,
            "user_avatar": post_user.avatar_url if post_user else None,
        })
    return output


@router.get("/posts/{post_id}", response_model=PostDetail)
async def get_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(CommunityPost).where(CommunityPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    user_result = await db.execute(select(User).where(User.id == post.user_id))
    post_user = user_result.scalar_one_or_none()

    comments_result = await db.execute(
        select(PostComment)
        .where(PostComment.post_id == post_id)
        .order_by(PostComment.created_at)
    )
    comments = comments_result.scalars().all()

    comment_list = []
    for c in comments:
        cu_result = await db.execute(select(User).where(User.id == c.user_id))
        cu = cu_result.scalar_one_or_none()
        comment_list.append({
            "id": c.id,
            "post_id": c.post_id,
            "user_id": c.user_id,
            "content": c.content,
            "parent_id": c.parent_id,
            "created_at": c.created_at,
            "user_nickname": cu.nickname if cu else None,
        })

    return {
        "id": post.id,
        "user_id": post.user_id,
        "content": post.content,
        "topic_tags": post.topic_tags,
        "likes_count": post.likes_count,
        "comments_count": post.comments_count,
        "is_pinned": post.is_pinned,
        "created_at": post.created_at,
        "user_nickname": post_user.nickname if post_user else None,
        "user_avatar": post_user.avatar_url if post_user else None,
        "comments": comment_list,
    }


@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(CommunityPost).where(CommunityPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.likes_count += 1
    await db.flush()

    return {"post_id": post_id, "likes_count": post.likes_count}


@router.post("/posts/{post_id}/comments", status_code=201)
async def add_comment(
    post_id: str,
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(CommunityPost).where(CommunityPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = PostComment(
        post_id=post_id,
        user_id=current_user.id,
        content=data.content,
        parent_id=data.parent_id,
    )
    db.add(comment)
    post.comments_count += 1
    await db.flush()

    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "user_id": comment.user_id,
        "content": comment.content,
        "parent_id": comment.parent_id,
        "created_at": comment.created_at.isoformat(),
        "user_nickname": current_user.nickname,
    }


@router.post("/checkin")
async def checkin(
    data: CheckinRequest | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    result = await db.execute(
        select(Checkin).where(
            Checkin.user_id == current_user.id,
            func.date(Checkin.checkin_date) == today,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return {
            "status": "already_checked_in",
            "checkin_date": today.isoformat(),
            "streak_count": existing.streak_count,
        }

    yesterday = date.today()  # simplified - would calculate actual yesterday
    prev_result = await db.execute(
        select(Checkin)
        .where(Checkin.user_id == current_user.id)
        .order_by(desc(Checkin.checkin_date))
        .limit(1)
    )
    prev = prev_result.scalar_one_or_none()

    streak = 1
    if prev and (today - prev.checkin_date).days == 1:
        streak = prev.streak_count + 1

    checkin = Checkin(
        user_id=current_user.id,
        checkin_date=today,
        streak_count=streak,
        mood=data.mood if data else None,
        note=data.note if data else None,
    )
    db.add(checkin)
    await db.flush()

    return {
        "status": "checked_in",
        "checkin_date": today.isoformat(),
        "streak_count": streak,
    }


@router.get("/checkin/status", response_model=CheckinStatus)
async def checkin_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    result = await db.execute(
        select(Checkin).where(
            Checkin.user_id == current_user.id,
            func.date(Checkin.checkin_date) == today,
        )
    )
    today_checkin = result.scalar_one_or_none()

    prev_result = await db.execute(
        select(Checkin)
        .where(Checkin.user_id == current_user.id)
        .order_by(desc(Checkin.checkin_date))
        .limit(1)
    )
    latest = prev_result.scalar_one_or_none()

    checked_in = today_checkin is not None
    streak = latest.streak_count if latest else 0

    today_data = None
    if today_checkin:
        today_data = {
            "checkin_date": today_checkin.checkin_date.isoformat(),
            "mood": today_checkin.mood,
            "note": today_checkin.note,
        }

    return CheckinStatus(
        checked_in=checked_in,
        streak_count=streak,
        today_checkin=today_data,
    )
