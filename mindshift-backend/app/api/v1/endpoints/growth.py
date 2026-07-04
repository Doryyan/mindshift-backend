from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.growth import GrowthStory, StoryLike
from app.models.expert_qa import ExpertQuestion
from app.services.growth.knowledge_cards import get_daily_card
from app.services.growth.share_cards import generate_share_card_data
from app.services.growth.public_courses import (
    get_current_week_course,
    get_all_courses,
)
from app.services.ai.zhipuai_service import zhipu_chat

router = APIRouter(prefix="/growth", tags=["growth"])

# =============================================================================
# KNOWLEDGE & SHARE CARDS (existing)
# =============================================================================


@router.get("/daily-card")
async def daily_knowledge_card(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get today's NLP knowledge card."""
    return get_daily_card()


@router.post("/share-card")
async def create_share_card(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate share card data for an achievement."""
    achievement_type = data.get("achievement_type")
    if not achievement_type:
        raise HTTPException(status_code=400, detail="achievement_type is required")

    user_info = {
        "nickname": current_user.nickname,
        "email": current_user.email,
    }

    user_data = {**user_info, **data.get("user_data", {})}
    return generate_share_card_data(achievement_type, user_data)


# =============================================================================
# PUBLIC COURSES (Task 1)
# =============================================================================


@router.get("/public-course")
async def get_public_course(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get this week's free public course."""
    return get_current_week_course()


@router.get("/public-course/history")
async def get_public_course_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all past public courses (summary only)."""
    return get_all_courses()


@router.post("/public-course/feedback")
async def submit_course_feedback(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback for a public course (rating + comment)."""
    rating = data.get("rating")
    comment = data.get("comment", "")
    topic = data.get("topic", "unknown")

    if rating is None or not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be a number between 1 and 5")

    # Log feedback (could be stored in DB or external analytics)
    from loguru import logger
    logger.info(
        f"Public course feedback: user={current_user.id}, topic={topic}, "
        f"rating={rating}, comment={comment}"
    )

    return {
        "message": "感谢你的反馈！你的意见帮助我们做得更好。",
        "rating": rating,
        "topic": topic,
    }


# =============================================================================
# GROWTH STORIES (Task 2)
# =============================================================================


@router.get("/stories")
async def list_growth_stories(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """List published growth stories (featured first, then by likes)."""
    offset = (page - 1) * limit

    # Get total count
    count_query = select(func.count()).select_from(GrowthStory).where(GrowthStory.is_published == True)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get stories ordered: featured first, then by likes
    query = (
        select(GrowthStory)
        .where(GrowthStory.is_published == True)
        .order_by(GrowthStory.is_featured.desc(), GrowthStory.likes_count.desc(), GrowthStory.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    stories = result.scalars().all()

    return {
        "stories": [
            {
                "id": s.id,
                "title": s.title,
                "content": s.content[:200] + "..." if len(s.content) > 200 else s.content,
                "tags": s.tags,
                "likes_count": s.likes_count,
                "is_featured": s.is_featured,
                "is_anonymous": s.is_anonymous,
                "author": "匿名用户" if s.is_anonymous else None,
                "user_id": s.user_id if not s.is_anonymous else None,
                "created_at": s.created_at.isoformat(),
            }
            for s in stories
        ],
        "total": total,
        "page": page,
        "has_more": offset + limit < total,
    }


@router.get("/stories/my")
async def list_my_stories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's submitted growth stories."""
    query = (
        select(GrowthStory)
        .where(GrowthStory.user_id == current_user.id)
        .order_by(GrowthStory.created_at.desc())
    )
    result = await db.execute(query)
    stories = result.scalars().all()

    return [
        {
            "id": s.id,
            "title": s.title,
            "content": s.content[:200] + "..." if len(s.content) > 200 else s.content,
            "tags": s.tags,
            "likes_count": s.likes_count,
            "is_featured": s.is_featured,
            "is_published": s.is_published,
            "is_anonymous": s.is_anonymous,
            "created_at": s.created_at.isoformat(),
        }
        for s in stories
    ]


@router.get("/stories/{story_id}")
async def get_story_detail(
    story_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get full story detail."""
    result = await db.execute(
        select(GrowthStory).where(
            and_(GrowthStory.id == story_id, GrowthStory.is_published == True)
        )
    )
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Get related stories (same tags, excluding current)
    related_stories = []
    if story.tags:
        # Get stories that share tags
        tag_values = list(story.tags.values()) if isinstance(story.tags, dict) else story.tags
        related_query = (
            select(GrowthStory)
            .where(
                and_(
                    GrowthStory.id != story.id,
                    GrowthStory.is_published == True,
                    GrowthStory.is_featured == True,
                )
            )
            .order_by(GrowthStory.likes_count.desc())
            .limit(3)
        )
        related_result = await db.execute(related_query)
        related = related_result.scalars().all()
        related_stories = [
            {
                "id": r.id,
                "title": r.title,
                "likes_count": r.likes_count,
                "tags": r.tags,
            }
            for r in related
        ]

    return {
        "id": story.id,
        "title": story.title,
        "content": story.content,
        "tags": story.tags,
        "likes_count": story.likes_count,
        "is_featured": story.is_featured,
        "is_anonymous": story.is_anonymous,
        "author": "匿名用户" if story.is_anonymous else None,
        "user_id": story.user_id if not story.is_anonymous else None,
        "created_at": story.created_at.isoformat(),
        "related_stories": related_stories,
    }


@router.post("/stories")
async def submit_growth_story(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a new growth story."""
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    tags = data.get("tags", [])
    is_anonymous = data.get("is_anonymous", False)

    if not title or not content:
        raise HTTPException(status_code=400, detail="Title and content are required")
    if len(content) < 50:
        raise HTTPException(status_code=400, detail="Content should be at least 50 characters")

    story = GrowthStory(
        user_id=current_user.id,
        title=title,
        content=content,
        tags=tags if isinstance(tags, dict) else {"techniques": tags} if isinstance(tags, list) else None,
        is_anonymous=is_anonymous,
        is_published=True,
    )
    db.add(story)
    await db.flush()

    return {
        "id": story.id,
        "title": story.title,
        "message": "你的成长故事已成功发布！感谢分享你的NLP学习心得。",
        "created_at": story.created_at.isoformat(),
    }


@router.post("/stories/{story_id}/like")
async def like_story(
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Like or unlike a growth story."""
    result = await db.execute(
        select(GrowthStory).where(GrowthStory.id == story_id)
    )
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Check if already liked
    like_result = await db.execute(
        select(StoryLike).where(
            and_(StoryLike.story_id == story_id, StoryLike.user_id == current_user.id)
        )
    )
    existing_like = like_result.scalar_one_or_none()

    if existing_like:
        # Unlike
        await db.delete(existing_like)
        story.likes_count = max(0, story.likes_count - 1)
        liked = False
    else:
        # Like
        like = StoryLike(story_id=story_id, user_id=current_user.id)
        db.add(like)
        story.likes_count += 1
        liked = True

    await db.flush()

    return {
        "liked": liked,
        "likes_count": story.likes_count,
    }


# =============================================================================
# EXPERT Q&A (Task 3)
# =============================================================================

QA_CATEGORIES = ["NLP技巧", "情绪管理", "人际关系", "学习困惑"]

AI_ANSWER_PROMPT = """你是一位专业的NLP（神经语言程序学）教练，正在回答用户的问题。

请以温暖、专业、实用的方式回答以下问题。回答应包括：
1. 问题的核心分析（50字以内）
2. 可以应用的NLP技巧或方法（至少2个）
3. 具体的行动建议
4. 一句鼓励的话

请用中文回答，控制在300字以内。不要在回复中包含本提示。

用户问题：{question}"""


@router.get("/qa")
async def list_qa_questions(
    category: Optional[str] = Query(None),
    answered: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """List expert Q&A questions with optional filters."""
    offset = (page - 1) * limit

    conditions = [True]  # Always true base condition
    if category and category in QA_CATEGORIES:
        conditions.append(ExpertQuestion.category == category)
    if answered is not None:
        conditions.append(ExpertQuestion.is_answered == answered)

    # Count
    count_query = (
        select(func.count())
        .select_from(ExpertQuestion)
        .where(and_(*conditions))
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Query
    query = (
        select(ExpertQuestion)
        .where(and_(*conditions))
        .order_by(ExpertQuestion.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    questions = result.scalars().all()

    return {
        "questions": [
            {
                "id": q.id,
                "title": q.title,
                "content": q.content[:150] + "..." if len(q.content) > 150 else q.content,
                "category": q.category,
                "is_answered": q.is_answered,
                "is_ai_answer": q.is_ai_answer,
                "answered_by": q.answered_by,
                "created_at": q.created_at.isoformat(),
            }
            for q in questions
        ],
        "total": total,
        "page": page,
        "has_more": offset + limit < total,
        "categories": QA_CATEGORIES,
    }


@router.get("/qa/{question_id}")
async def get_qa_detail(
    question_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get question detail with answer."""
    result = await db.execute(
        select(ExpertQuestion).where(ExpertQuestion.id == question_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    return {
        "id": question.id,
        "title": question.title,
        "content": question.content,
        "category": question.category,
        "is_answered": question.is_answered,
        "is_ai_answer": question.is_ai_answer,
        "answer_content": question.answer_content,
        "answered_by": question.answered_by,
        "answered_at": question.answered_at.isoformat() if question.answered_at else None,
        "created_at": question.created_at.isoformat(),
    }


@router.post("/qa")
async def submit_qa_question(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a new expert Q&A question. AI auto-answers basic questions."""
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    category = data.get("category", "NLP技巧")

    if not title or not content:
        raise HTTPException(status_code=400, detail="Title and content are required")
    if len(content) < 20:
        raise HTTPException(status_code=400, detail="Content should be at least 20 characters")
    if category not in QA_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Category must be one of: {', '.join(QA_CATEGORIES)}")

    # Create question
    question = ExpertQuestion(
        user_id=current_user.id,
        title=title,
        content=content,
        category=category,
    )
    db.add(question)
    await db.flush()

    # Attempt AI auto-answer
    ai_answer = None
    try:
        prompt = AI_ANSWER_PROMPT.format(question=f"{title}\n{content}")
        ai_response = await zhipu_chat(
            messages=[{"role": "user", "content": prompt}],
            model="glm-4-flash",
            temperature=0.7,
            max_tokens=500,
        )
        if ai_response:
            raw = ai_response.get("raw_response", "")
            if raw:
                ai_answer = f"🤖 AI初步回答（待专家审核）\n\n{raw}\n\n---\n*此回答由AI自动生成，仅供参考。NLP专家将进行审核和补充。*"
                question.answer_content = ai_answer
                question.is_answered = True
                question.is_ai_answer = True
                question.answered_by = "AI助手"
                question.answered_at = datetime.now(timezone.utc)
                await db.flush()
    except Exception:
        from loguru import logger
        logger.warning(f"AI auto-answer failed for question {question.id}")

    return {
        "id": question.id,
        "title": question.title,
        "message": "你的问题已提交成功！",
        "has_ai_answer": ai_answer is not None,
        "created_at": question.created_at.isoformat(),
    }


@router.post("/qa/{question_id}/answer")
async def answer_question(
    question_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Answer a question (admin/expert only placeholder)."""
    result = await db.execute(
        select(ExpertQuestion).where(ExpertQuestion.id == question_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    answer_content = data.get("answer_content", "").strip()
    if not answer_content:
        raise HTTPException(status_code=400, detail="answer_content is required")

    question.answer_content = answer_content
    question.is_answered = True
    question.is_ai_answer = False
    question.answered_by = current_user.nickname
    question.answered_at = datetime.now(timezone.utc)
    await db.flush()

    return {
        "id": question.id,
        "message": "回答已发布",
        "answered_by": question.answered_by,
        "answered_at": question.answered_at.isoformat(),
    }
