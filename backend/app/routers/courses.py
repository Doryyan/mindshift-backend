from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.course import Course, Lesson, KnowledgeCard
from app.models.user import UserProgress
from app.utils.security import get_current_user
from app.models.user import User
from typing import Optional

router = APIRouter(prefix="/api/v1/courses", tags=["Courses"])

@router.get("")
async def list_courses(
    category: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Course).where(Course.is_public == False).order_by(Course.sort_order, Course.created_at.desc())
    if category: q = q.where(Course.category == category)
    if level: q = q.where(Course.level == level)
    result = await db.execute(q)
    courses = result.scalars().all()
    return courses

@router.get("/{course_id}")
async def get_course(course_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course: raise HTTPException(404, "课程不存在")
    lessons_result = await db.execute(select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.sort_order))
    lessons = lessons_result.scalars().all()
    return {"course": course, "lessons": lessons}

@router.get("/{course_id}/lessons/{lesson_id}")
async def get_lesson(
    course_id: str, lesson_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Lesson).where(Lesson.id == lesson_id, Lesson.course_id == course_id))
    lesson = r.scalar_one_or_none()
    if not lesson: raise HTTPException(404, "课程内容不存在")
    pr = await db.execute(select(UserProgress).where(
        UserProgress.user_id == user.id, UserProgress.lesson_id == lesson_id
    ))
    progress = pr.scalar_one_or_none()
    return {"lesson": lesson, "progress": progress}

@router.post("/{course_id}/lessons/{lesson_id}/complete")
async def complete_lesson(
    course_id: str, lesson_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime, timezone
    r = await db.execute(select(UserProgress).where(
        UserProgress.user_id == user.id, UserProgress.lesson_id == lesson_id
    ))
    progress = r.scalar_one_or_none()
    if not progress:
        progress = UserProgress(user_id=user.id, course_id=course_id, lesson_id=lesson_id)
        db.add(progress)
    progress.completed = True
    progress.completed_at = datetime.now(timezone.utc)
    progress.progress_pct = 100.0
    await db.flush()
    return {"success": True, "message": "已标记完成"}

@router.get("/public/all")
async def list_public_courses(
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Course).where(Course.is_public == True).order_by(Course.sort_order, Course.created_at.desc())
    if category: q = q.where(Course.category == category)
    result = await db.execute(q)
    return result.scalars().all()

@router.get("/public/{course_id}")
async def get_public_course(course_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course).where(Course.id == course_id, Course.is_public == True))
    course = result.scalar_one_or_none()
    if not course: raise HTTPException(404, "课程不存在")
    lessons_result = await db.execute(select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.sort_order))
    return {"course": course, "lessons": lessons_result.scalars().all()}

@router.get("/knowledge/today")
async def get_daily_knowledge(db: AsyncSession = Depends(get_db)):
    from datetime import date
    today = date.today().isoformat()
    r = await db.execute(select(KnowledgeCard).where(KnowledgeCard.date == today).order_by(KnowledgeCard.created_at.desc()).limit(1))
    card = r.scalar_one_or_none()
    if not card:
        # Fallback: return the latest card
        r = await db.execute(select(KnowledgeCard).order_by(KnowledgeCard.created_at.desc()).limit(1))
        card = r.scalar_one_or_none()
    return {"card": card} if card else {"card": None}
