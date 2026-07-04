from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import NlpCourse
from app.models.membership import NlpSkillProfile
from app.models.roleplay import RpScenario, RpDialogueSession
from app.models.user import User

# Map skill profile dimensions to search keywords for courses/scenarios
DIMENSION_KEYWORDS = {
    "sensory_acuity": ["感官", "表象", "VAKOG", "五感", "觉察", "观察"],
    "rapport_building": ["亲和力", "匹配", "米尔顿", "同步", "连接", "信任"],
    "belief_transformation": ["信念", "转化", "限制性", "重构", "核心信念", "转变"],
    "submodality_mastery": ["次感元", "映射", "内在", "体验", "重塑", "表象"],
    "language_pattern": ["语言", "模式", "元模型", "提问", "沟通", "话术"],
    "state_management": ["状态", "心锚", "情绪", "管理", "掌控", "调节"],
    "anchoring_skill": ["心锚", "锚定", "条件", "触发", "连接", "状态"],
    "reframing_skill": ["换框", "重构", "视角", "意义", "灵活", "转变"],
}


def _score_course(course: NlpCourse, weak_dimensions: list[str]) -> float:
    """Score a course based on how well it matches weak dimensions."""
    score = 0.0
    tags = course.tags or {}
    all_tag_text = " ".join(
        tag for tag_list in tags.values() for tag in tag_list
    )
    for dim in weak_dimensions:
        keywords = DIMENSION_KEYWORDS.get(dim, [])
        for kw in keywords:
            if kw in course.title or kw in (course.description or ""):
                score += 3.0
            if kw in all_tag_text:
                score += 2.0
    return score


def _score_scenario(scenario: RpScenario, weak_dimensions: list[str]) -> float:
    """Score a scenario based on how well it matches weak dimensions."""
    score = 0.0
    nlp_techniques = scenario.nlp_techniques or {}
    all_tech_values = " ".join(
        v for v_list in nlp_techniques.values() for v in v_list
    ) if isinstance(nlp_techniques, dict) else ""
    for dim in weak_dimensions:
        keywords = DIMENSION_KEYWORDS.get(dim, [])
        for kw in keywords:
            if kw in scenario.title or kw in (scenario.description or ""):
                score += 3.0
            if kw in all_tech_values:
                score += 2.0
            if kw in str(scenario.category):
                score += 1.0
    return score


async def get_recommended_courses(
    db: AsyncSession, user_id: str, limit: int = 3
) -> list[dict]:
    """
    Return recommended courses based on the user's weakest skill dimensions.
    If no skill profile exists, return the most popular beginner courses.
    """
    result = await db.execute(
        select(NlpSkillProfile).where(NlpSkillProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        result = await db.execute(
            select(NlpCourse)
            .where(NlpCourse.level == "beginner")
            .order_by(NlpCourse.sort_order)
            .limit(limit)
        )
        courses = result.scalars().all()
        return [_course_to_dict(c) for c in courses]

    # Find the 2-3 lowest scoring dimensions
    dimensions = {
        "sensory_acuity": profile.sensory_acuity,
        "rapport_building": profile.rapport_building,
        "belief_transformation": profile.belief_transformation,
        "submodality_mastery": profile.submodality_mastery,
        "language_pattern": profile.language_pattern,
        "state_management": profile.state_management,
        "anchoring_skill": profile.anchoring_skill,
        "reframing_skill": profile.reframing_skill,
    }
    sorted_dims = sorted(dimensions.items(), key=lambda x: x[1])
    weak_dims = [dim for dim, _ in sorted_dims[:3]]

    # Fetch all courses and score them
    result = await db.execute(select(NlpCourse))
    all_courses = result.scalars().all()

    scored = [
        (_score_course(course, weak_dims), course) for course in all_courses
    ]
    scored.sort(key=lambda x: x[0], reverse=True)

    recommended = [course for _, course in scored[:limit]]
    return [_course_to_dict(c) for c in recommended]


async def get_recommended_scenarios(
    db: AsyncSession, user_id: str, limit: int = 3
) -> list[dict]:
    """
    Return recommended scenarios based on skill weaknesses and user interests.
    Excludes already completed scenarios.
    """
    # Get user profile and preferences
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    interests = []
    if user and user.preferences:
        interests = user.preferences.get("interests", [])

    result = await db.execute(
        select(NlpSkillProfile).where(NlpSkillProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()

    # Get completed scenario IDs
    result = await db.execute(
        select(RpDialogueSession.scenario_id)
        .where(
            RpDialogueSession.user_id == user_id,
            RpDialogueSession.status == "completed",
        )
    )
    completed_ids = {row[0] for row in result.all()}

    if not profile:
        result = await db.execute(
            select(RpScenario)
            .where(RpScenario.difficulty == "easy")
            .limit(limit)
        )
        scenarios = result.scalars().all()
        return [_scenario_to_dict(s) for s in scenarios if s.id not in completed_ids]

    # Find weak dimensions
    dimensions = {
        "sensory_acuity": profile.sensory_acuity,
        "rapport_building": profile.rapport_building,
        "belief_transformation": profile.belief_transformation,
        "submodality_mastery": profile.submodality_mastery,
        "language_pattern": profile.language_pattern,
        "state_management": profile.state_management,
        "anchoring_skill": profile.anchoring_skill,
        "reframing_skill": profile.reframing_skill,
    }
    sorted_dims = sorted(dimensions.items(), key=lambda x: x[1])
    weak_dims = [dim for dim, _ in sorted_dims[:3]]

    # Fetch all scenarios and score
    result = await db.execute(select(RpScenario))
    all_scenarios = result.scalars().all()

    # Filter out completed
    candidates = [s for s in all_scenarios if s.id not in completed_ids]

    # Boost scenarios matching user interests
    scored = []
    for scenario in candidates:
        score = _score_scenario(scenario, weak_dims)
        # Boost if scenario category matches user interests
        category = scenario.category or ""
        for interest in interests:
            if interest in category:
                score += 5.0
        scored.append((score, scenario))

    scored.sort(key=lambda x: x[0], reverse=True)
    recommended = [scenario for _, scenario in scored[:limit]]
    return [_scenario_to_dict(s) for s in recommended]


def _course_to_dict(course: NlpCourse) -> dict:
    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "level": course.level,
        "source": course.source,
        "lesson_count": course.lesson_count,
        "duration_minutes": course.duration_minutes,
        "tags": course.tags,
        "cover_emoji": course.cover_emoji,
        "is_premium": course.is_premium,
        "sort_order": course.sort_order,
    }


def _scenario_to_dict(scenario: RpScenario) -> dict:
    return {
        "id": scenario.id,
        "category": scenario.category,
        "title": scenario.title,
        "description": scenario.description,
        "difficulty": scenario.difficulty,
        "nlp_techniques": scenario.nlp_techniques,
        "is_premium": scenario.is_premium,
    }
