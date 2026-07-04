from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.case import Case
from typing import Optional

router = APIRouter(prefix="/api/v1/cases", tags=["Cases"])

@router.get("")
async def list_cases(
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Case).order_by(Case.sort_order, Case.created_at.desc())
    if category: q = q.where(Case.category == category)
    result = await db.execute(q)
    return result.scalars().all()

@router.get("/{case_id}")
async def get_case(case_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Case).where(Case.id == case_id))
    case = r.scalar_one_or_none()
    if not case: raise HTTPException(404, "案例不存在")
    return case
