from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.case import NlpCase
from app.models.user import User

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("")
async def list_cases(
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(NlpCase)
    if category:
        query = query.where(NlpCase.category == category)
    result = await db.execute(query)
    cases = result.scalars().all()
    return [
        {
            "id": c.id,
            "title": c.title,
            "category": c.category,
            "scenario_description": c.scenario_description,
            "techniques_applied": c.techniques_applied,
            "key_learning": c.key_learning,
            "is_premium": c.is_premium,
        }
        for c in cases
    ]


@router.get("/{case_id}")
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(NlpCase).where(NlpCase.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return {
        "id": case.id,
        "title": case.title,
        "category": case.category,
        "scenario_description": case.scenario_description,
        "problem_analysis": case.problem_analysis,
        "techniques_applied": case.techniques_applied,
        "before_state": case.before_state,
        "after_state": case.after_state,
        "key_learning": case.key_learning,
        "source": case.source,
        "is_premium": case.is_premium,
        "created_at": case.created_at.isoformat(),
    }
