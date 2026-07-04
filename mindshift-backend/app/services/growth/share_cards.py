from __future__ import annotations

from datetime import datetime
from typing import Any


def generate_share_card_data(achievement_type: str, user_data: dict[str, Any]) -> dict[str, Any]:
    """Generate share card data for different achievement types.

    Achievement types:
    - "first_course_complete": {course_name, date, lessons_completed}
    - "streak_21_days": {streak_days, start_date}
    - "belt_promotion": {old_belt, new_belt, radar_scores}
    - "roleplay_victory": {scenario_title, nlp_techniques_used, score}
    - "training_milestone": {training_count, training_type}
    """
    base = {
        "achievement_type": achievement_type,
        "brand": "念转 MindShift",
        "generated_at": datetime.utcnow().isoformat(),
    }

    handlers = {
        "first_course_complete": _first_course_complete,
        "streak_21_days": _streak_21_days,
        "belt_promotion": _belt_promotion,
        "roleplay_victory": _roleplay_victory,
        "training_milestone": _training_milestone,
    }

    handler = handlers.get(achievement_type)
    if handler is None:
        return {**base, "error": f"Unknown achievement type: {achievement_type}"}

    card_data = handler(user_data)
    return {**base, **card_data}


def _first_course_complete(data: dict[str, Any]) -> dict[str, Any]:
    course_name = data.get("course_name", "未知课程")
    date = data.get("date", "")
    lessons_completed = data.get("lessons_completed", 0)

    quotes = [
        "每一次学习都是一次心智的升级。",
        "语言是思维的地图——改变语言，改变世界。",
        "NLP 的核心信念：身心是同一个系统。",
    ]
    import hashlib
    idx = int(hashlib.md5(course_name.encode()).hexdigest(), 16) % len(quotes)

    return {
        "title": "首次完成课程",
        "subtitle": f"恭喜完成《{course_name}》",
        "stats": [
            {"label": "学习课数", "value": str(lessons_completed)},
            {"label": "完成日期", "value": date or datetime.utcnow().strftime("%Y-%m-%d")},
        ],
        "quote": quotes[idx],
        "quote_author": "念转 MindShift",
    }


def _streak_21_days(data: dict[str, Any]) -> dict[str, Any]:
    streak_days = data.get("streak_days", 21)
    start_date = data.get("start_date", "")

    return {
        "title": f"连续坚持 {streak_days} 天",
        "subtitle": "祝贺你养成了每日觉察的好习惯",
        "stats": [
            {"label": "连续天数", "value": str(streak_days)},
            {"label": "开始日期", "value": start_date or datetime.utcnow().strftime("%Y-%m-%d")},
        ],
        "quote": "习惯不是一天养成的，而是每一天的选择。",
        "quote_author": "念转 MindShift",
    }


def _belt_promotion(data: dict[str, Any]) -> dict[str, Any]:
    old_belt = data.get("old_belt", "")
    new_belt = data.get("new_belt", "")
    radar_scores = data.get("radar_scores", {})

    top_skills = sorted(
        radar_scores.items(), key=lambda x: x[1], reverse=True
    )[:3] if radar_scores else []

    skill_labels = {
        "sensory_acuity": "感官觉察",
        "rapport_building": "亲和力",
        "belief_transformation": "信念转化",
        "submodality_mastery": "次感元掌握",
        "language_pattern": "语言模式",
        "state_management": "状态管理",
        "anchoring_skill": "锚定技巧",
        "reframing_skill": "换框能力",
    }

    top_skill_text = "、".join(
        skill_labels.get(s, s) for s, _ in top_skills
    ) if top_skills else "综合能力"

    return {
        "title": "段位晋升",
        "subtitle": f"从「{old_belt}」晋升为「{new_belt}」",
        "stats": [
            {"label": "旧段位", "value": old_belt or "-"},
            {"label": "新段位", "value": new_belt or "-"},
            {"label": "核心优势", "value": top_skill_text},
        ],
        "quote": "你今天的语言模式，决定明天的世界模样。",
        "quote_author": "理查·班德勒",
    }


def _roleplay_victory(data: dict[str, Any]) -> dict[str, Any]:
    scenario_title = data.get("scenario_title", "角色扮演")
    nlp_techniques = data.get("nlp_techniques_used", [])
    score = data.get("score", 0)

    techniques_str = "、".join(nlp_techniques[:3]) if nlp_techniques else "综合技巧"

    return {
        "title": "角色扮演胜利",
        "subtitle": f"在「{scenario_title}」中表现出色",
        "stats": [
            {"label": "场景", "value": scenario_title},
            {"label": "得分", "value": f"{score}分"},
            {"label": "运用技巧", "value": techniques_str},
        ],
        "quote": "真正的改变始于觉察，成于练习。",
        "quote_author": "念转 MindShift",
    }


def _training_milestone(data: dict[str, Any]) -> dict[str, Any]:
    training_count = data.get("training_count", 0)
    training_type = data.get("training_type", "综合训练")

    return {
        "title": "训练里程碑",
        "subtitle": f"已完成 {training_count} 次{training_type}",
        "stats": [
            {"label": "训练次数", "value": str(training_count)},
            {"label": "训练类型", "value": training_type},
        ],
        "quote": "刻意练习是把潜能转化为能力的唯一路径。",
        "quote_author": "念转 MindShift",
    }
