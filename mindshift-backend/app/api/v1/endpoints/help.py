from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.help import HelpArticle
from app.models.user import User

router = APIRouter(prefix="/help", tags=["help"])


@router.get("/categories")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(HelpArticle.category, func.count(HelpArticle.id))
        .where(HelpArticle.is_published == True)
        .group_by(HelpArticle.category)
        .order_by(HelpArticle.category)
    )
    rows = result.all()
    return [
        {"category": row[0], "count": row[1]}
        for row in rows
    ]


@router.get("/articles")
async def list_articles(
    category: str | None = Query(None, description="Filter by category"),
    keyword: str | None = Query(None, description="Search by keyword in title or content"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(HelpArticle).where(HelpArticle.is_published == True)

    if category:
        query = query.where(HelpArticle.category == category)

    if keyword:
        search = f"%{keyword}%"
        query = query.where(
            HelpArticle.title.ilike(search) | HelpArticle.content.ilike(search)
        )

    query = query.order_by(HelpArticle.sort_order, HelpArticle.title)
    result = await db.execute(query)
    articles = result.scalars().all()

    return [
        {
            "id": a.id,
            "title": a.title,
            "category": a.category,
            "keywords": a.keywords,
            "sort_order": a.sort_order,
            "is_published": a.is_published,
            "created_at": a.created_at.isoformat(),
        }
        for a in articles
    ]


@router.get("/articles/{article_id}")
async def get_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(HelpArticle).where(HelpArticle.id == article_id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Help article not found")

    return {
        "id": article.id,
        "title": article.title,
        "category": article.category,
        "content": article.content,
        "keywords": article.keywords,
        "sort_order": article.sort_order,
        "is_published": article.is_published,
        "created_at": article.created_at.isoformat(),
        "updated_at": article.updated_at.isoformat(),
    }
