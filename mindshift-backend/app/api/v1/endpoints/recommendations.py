from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.recommendation import (
    get_recommended_courses,
    get_recommended_scenarios,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/courses")
async def recommended_courses(
    limit: int = Query(3, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    courses = await get_recommended_courses(db, current_user.id, limit=limit)
    return {"courses": courses}


@router.get("/scenarios")
async def recommended_scenarios(
    limit: int = Query(3, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scenarios = await get_recommended_scenarios(db, current_user.id, limit=limit)
    return {"scenarios": scenarios}
