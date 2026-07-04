from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.course import Course
from app.models.roleplay import Scenario
from app.models.user import User
from app.utils.security import get_optional_user
from typing import Optional

router = APIRouter(prefix="/api/v1/recommendations", tags=["Recommendations"])

@router.get("/courses")
async def recommend_courses(
    limit: int = Query(3, ge=1, le=10),
    user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(Course).where(Course.is_public == False).order_by(Course.sort_order).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()

@router.get("/scenarios")
async def recommend_scenarios(
    limit: int = Query(3, ge=1, le=10),
    user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(Scenario).order_by(Scenario.sort_order).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()
