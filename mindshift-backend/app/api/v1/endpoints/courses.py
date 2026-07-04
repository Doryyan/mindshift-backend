from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.course import NlpCourse, NlpLesson
from app.models.user import User
from app.schemas.course import CourseDetail, CourseListItem, LessonResponse
from app.services.membership.gate import get_user_membership_level

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseListItem])
async def list_courses(
    level: str | None = Query(None, description="Filter by level"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(NlpCourse).order_by(NlpCourse.sort_order)
    if level:
        query = query.where(NlpCourse.level == level)
    result = await db.execute(query)
    courses = result.scalars().all()

    # Filter premium courses for free users
    user_level = await get_user_membership_level(current_user.id)
    if user_level == "free":
        courses = [c for c in courses if not c.is_premium]

    return courses


@router.get("/{course_id}", response_model=CourseDetail)
async def get_course(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(NlpCourse)
        .options(selectinload(NlpCourse.lessons))
        .where(NlpCourse.id == course_id)
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Block premium course access for free users
    if course.is_premium:
        user_level = await get_user_membership_level(current_user.id)
        if user_level == "free":
            raise HTTPException(
                status_code=403,
                detail="This course requires a paid membership",
            )

    return course


@router.get("/{course_id}/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    course_id: str,
    lesson_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(NlpLesson).where(
            NlpLesson.course_id == course_id, NlpLesson.id == lesson_id
        )
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Check if course is premium and user has access
    course_result = await db.execute(
        select(NlpCourse).where(NlpCourse.id == course_id)
    )
    course = course_result.scalar_one_or_none()
    if course and course.is_premium:
        user_level = await get_user_membership_level(current_user.id)
        if user_level == "free":
            raise HTTPException(
                status_code=403,
                detail="This lesson requires a paid membership",
            )

    return lesson


@router.post("/{course_id}/lessons/{lesson_id}/complete")
async def complete_lesson(
    course_id: str,
    lesson_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(NlpLesson).where(
            NlpLesson.course_id == course_id, NlpLesson.id == lesson_id
        )
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    return {"status": "completed", "lesson_id": lesson_id, "user_id": current_user.id}
