from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User, UserProgress
from app.models.training import TrainingSession, Achievement, UserAchievement
from app.models.roleplay import RoleplaySession
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/progress", tags=["Progress"])

@router.get("")
async def get_progress(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Course progress
    completed_lessons = (await db.execute(
        select(func.count(UserProgress.id)).where(UserProgress.user_id == user.id, UserProgress.completed == True)
    )).scalar() or 0
    
    # Training count
    training_count = (await db.execute(
        select(func.count(TrainingSession.id)).where(TrainingSession.user_id == user.id)
    )).scalar() or 0
    
    # Roleplay count
    roleplay_count = (await db.execute(
        select(func.count(RoleplaySession.id)).where(RoleplaySession.user_id == user.id)
    )).scalar() or 0
    
    return {
        "level": user.level,
        "xp": user.xp,
        "completed_lessons": completed_lessons,
        "training_count": training_count,
        "roleplay_count": roleplay_count,
    }

@router.get("/radar")
async def get_radar(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Radar chart data for NLP skill dimensions."""
    # Calculate scores based on user's activity
    training_count = (await db.execute(
        select(func.count(TrainingSession.id)).where(TrainingSession.user_id == user.id)
    )).scalar() or 0
    
    roleplay_count = (await db.execute(
        select(func.count(RoleplaySession.id)).where(RoleplaySession.user_id == user.id)
    )).scalar() or 0
    
    completed_lessons = (await db.execute(
        select(func.count(UserProgress.id)).where(UserProgress.user_id == user.id, UserProgress.completed == True)
    )).scalar() or 0
    
    # Map to 6 NLP skill dimensions (0-100)
    def scale(v, max_v=20): return min(100, int(v / max_v * 100))
    
    return {
        "dimensions": [
            {"name": "感官觉察", "score": scale(training_count, 15), "max": 100},
            {"name": "信念转变", "score": scale(completed_lessons, 25), "max": 100},
            {"name": "沟通技巧", "score": scale(roleplay_count, 10), "max": 100},
            {"name": "情绪管理", "score": scale(training_count // 2 + completed_lessons // 2, 15), "max": 100},
            {"name": "目标设定", "score": scale(completed_lessons // 2, 10), "max": 100},
            {"name": "关系建立", "score": scale(roleplay_count, 10), "max": 100},
        ]
    }

@router.get("/achievements")
async def get_achievements(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    all_achievements = (await db.execute(select(Achievement))).scalars().all()
    user_achievements = (await db.execute(
        select(UserAchievement).where(UserAchievement.user_id == user.id)
    )).scalars().all()
    unlocked_ids = {ua.achievement_id for ua in user_achievements}
    
    result = []
    for a in all_achievements:
        result.append({
            "id": a.id, "key": a.key, "name": a.name, "description": a.description,
            "icon": a.icon, "category": a.category, "xp_reward": a.xp_reward,
            "unlocked": a.id in unlocked_ids,
        })
    return result
