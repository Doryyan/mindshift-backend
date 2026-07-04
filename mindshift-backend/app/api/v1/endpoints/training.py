from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.training import NlpTrainingRecord
from app.models.user import User
from app.schemas.training import (
    TrainingEvaluateRequest,
    TrainingRecordResponse,
    BeliefMineRequest,
    MeditationGenerateRequest,
    DreamAnalyzeRequest,
)
from app.services.nlp.evaluator import evaluate_training
from app.services.nlp.belief_miner import mine_beliefs
from app.services.nlp.meditation_guide import generate_meditation
from app.services.nlp.affirmation import generate_daily_affirmation
from app.services.nlp.dream_analyzer import analyze_dream

router = APIRouter(prefix="/training", tags=["training"])


@router.post("/evaluate")
async def evaluate(
    data: TrainingEvaluateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ai_result = await evaluate_training(data.training_type, data.input_data)

    overall_score = None
    if ai_result and isinstance(ai_result, dict):
        overall_score = ai_result.get("overall_score")

    record = NlpTrainingRecord(
        user_id=current_user.id,
        training_type=data.training_type,
        input_data=data.input_data,
        ai_result=ai_result,
        overall_score=overall_score,
        time_spent_seconds=0,
    )
    db.add(record)
    await db.flush()

    return {
        "id": record.id,
        "training_type": record.training_type,
        "input_data": record.input_data,
        "ai_result": record.ai_result,
        "overall_score": record.overall_score,
        "created_at": record.created_at.isoformat(),
    }


@router.get("/records", response_model=list[TrainingRecordResponse])
async def get_records(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(NlpTrainingRecord)
        .where(NlpTrainingRecord.user_id == current_user.id)
        .order_by(desc(NlpTrainingRecord.created_at))
        .limit(50)
    )
    return result.scalars().all()


@router.post("/belief/mine")
async def belief_mine(
    data: BeliefMineRequest,
    current_user: User = Depends(get_current_user),
):
    """Mine limiting beliefs from user input using NLP belief analysis."""
    result = await mine_beliefs(data.user_input)
    if result is None:
        raise HTTPException(
            status_code=422,
            detail="无法分析该输入。请提供更详细的描述（至少10个字符）。",
        )
    return result


@router.post("/meditation")
async def meditation_generate(
    data: MeditationGenerateRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate a personalized NLP guided meditation script."""
    result = await generate_meditation(data.state, data.focus)
    if result is None:
        raise HTTPException(
            status_code=422,
            detail="无法生成冥想引导。请提供有效的情绪状态和聚焦领域。",
        )
    return result


@router.get("/daily-affirmation")
async def daily_affirmation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a personalized daily affirmation based on recent training data."""
    # Gather user training stats
    result = await db.execute(
        select(NlpTrainingRecord)
        .where(NlpTrainingRecord.user_id == current_user.id)
        .order_by(desc(NlpTrainingRecord.created_at))
        .limit(50)
    )
    records = result.scalars().all()

    # Build stats from records
    training_types = [r.training_type for r in records]
    scores = [r.overall_score for r in records if r.overall_score is not None]
    unique_types = list(set(training_types))

    from collections import Counter
    type_counter = Counter(training_types)
    top_type = type_counter.most_common(1)[0][0] if type_counter else ""

    # Calculate consecutive days
    consecutive_days = 0
    from datetime import datetime, timezone
    if records:
        today = datetime.now(timezone.utc).date()
        seen_dates = set()
        for r in records:
            record_date = r.created_at.date()
            seen_dates.add(record_date)
        # Count consecutive days from today going backwards
        check_date = today
        while check_date in seen_dates:
            consecutive_days += 1
            check_date = check_date.replace(day=check_date.day - 1)

    user_stats = {
        "total_days": len(records),
        "consecutive_days": consecutive_days,
        "recent_training_types": unique_types[:5],
        "average_score": round(sum(scores) / len(scores), 1) if scores else None,
        "last_training_type": top_type,
        "top_skill": _type_to_skill(top_type),
    }

    result_affirm = await generate_daily_affirmation(user_stats)
    if result_affirm is None:
        raise HTTPException(
            status_code=500,
            detail="生成每日肯定语失败，请稍后重试。",
        )
    return result_affirm


@router.post("/dream/analyze")
async def dream_analyze(
    data: DreamAnalyzeRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze a dream from NLP submodality perspective."""
    result = await analyze_dream(data.dream_text)
    if result is None:
        raise HTTPException(
            status_code=422,
            detail="无法分析该梦境。请提供更详细的描述（至少20个字符）。",
        )
    return result


def _type_to_skill(training_type: str) -> str:
    """Map training type to human-readable skill name."""
    skill_map = {
        "sensory": "感官觉察",
        "belief": "信念转化",
        "anchor": "心锚技术",
        "language": "语言模式",
        "quiz": "知识掌握",
        "submodality": "次感元调节",
        "reframing": "换框能力",
    }
    return skill_map.get(training_type, "综合练习")
