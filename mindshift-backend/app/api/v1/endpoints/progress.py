from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.membership import NlpSkillProfile
from app.models.training import NlpTrainingRecord
from app.models.roleplay import RpDialogueSession
from app.models.user import User

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/summary")
async def progress_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_trainings = await db.scalar(
        select(func.count()).where(NlpTrainingRecord.user_id == current_user.id)
    )
    total_roleplays = await db.scalar(
        select(func.count()).where(RpDialogueSession.user_id == current_user.id)
    )

    avg_score = await db.scalar(
        select(func.avg(NlpTrainingRecord.overall_score)).where(
            NlpTrainingRecord.user_id == current_user.id,
            NlpTrainingRecord.overall_score.isnot(None),
        )
    )

    result = await db.execute(
        select(NlpSkillProfile).where(NlpSkillProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    return {
        "total_trainings": total_trainings or 0,
        "total_roleplays": total_roleplays or 0,
        "average_score": round(float(avg_score or 0), 1),
        "streak_days": profile.streak_days if profile else 0,
        "user_stage": current_user.stage,
    }


@router.get("/radar")
async def progress_radar(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(NlpSkillProfile).where(NlpSkillProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        return {
            "sensory_acuity": 0,
            "rapport_building": 0,
            "belief_transformation": 0,
            "submodality_mastery": 0,
            "language_pattern": 0,
            "state_management": 0,
            "anchoring_skill": 0,
            "reframing_skill": 0,
        }

    return {
        "sensory_acuity": profile.sensory_acuity,
        "rapport_building": profile.rapport_building,
        "belief_transformation": profile.belief_transformation,
        "submodality_mastery": profile.submodality_mastery,
        "language_pattern": profile.language_pattern,
        "state_management": profile.state_management,
        "anchoring_skill": profile.anchoring_skill,
        "reframing_skill": profile.reframing_skill,
    }
