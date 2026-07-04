from __future__ import annotations

from loguru import logger

from app.services.ai.zhipuai_service import zhipu_chat

DAILY_AFFIRMATION_PROMPT = """你是一位NLP积极心理学教练，擅长根据用户的学习和训练数据生成个性化的每日肯定语。

请根据用户的近期训练数据统计，生成当天的练习内容：

生成要求：
1. affirmation（每日肯定语）：40字以内的一句话，既要肯定当前的进步，又要激发进一步成长。使用NLP风格的正面语言——避免否定词，用积极陈述替代。
2. focus_tip（今日聚焦提示）：20字以内的简短提醒，告诉用户今天可以把注意力放在哪个NLP技能的练习上。
3. nlp_quote（NLP名言）：选择或创作一句NLP相关的名言或智慧语句，附上出处说明。名言应深刻而有启发性。
4. mini_challenge（迷你挑战）：一个简单的、可以在今天完成的小练习挑战，把NLP技能融入日常生活。

生成原则：
- 肯定语要具体且个性化，结合用户近期的训练类型
- 语言积极、有力量，避免空洞的鸡汤
- 迷你挑战要具体可操作，不是泛泛的建议
- 如果用户近期有进步数据（连续训练天数、评分提升等），要在内容中体现鼓励
- 如果是新用户（数据较少），内容要温和、鼓励性，不施加压力

请严格按照以下JSON格式返回：
{
  "affirmation": "40字以内的每日肯定语",
  "focus_tip": "20字以内的今日聚焦提示",
  "nlp_quote": {
    "text": "NLP名言内容",
    "attribution": "出处/作者"
  },
  "mini_challenge": {
    "title": "今日迷你挑战标题",
    "description": "今天可以完成的NLP小练习描述",
    "duration_hint": "建议用时（如：3分钟）"
  }
}"""


async def generate_daily_affirmation(user_stats: dict) -> dict | None:
    """Generate a personalized daily affirmation based on user's training data.

    Args:
        user_stats: Dict with user's recent training statistics, e.g.:
            {
                "total_days": 14,
                "consecutive_days": 7,
                "recent_training_types": ["sensory", "belief"],
                "average_score": 72,
                "last_training_type": "sensory",
                "top_skill": "感官觉察",
            }

    Returns:
        Dict with affirmation, focus_tip, nlp_quote, mini_challenge
        or None if generation fails
    """
    if not user_stats:
        logger.warning("Empty user stats for daily affirmation")
        user_stats = {"total_days": 0, "consecutive_days": 0}

    stats_summary = _format_stats(user_stats)

    messages = [
        {"role": "system", "content": DAILY_AFFIRMATION_PROMPT},
        {
            "role": "user",
            "content": f"用户近期训练数据：\n{stats_summary}\n\n请生成今日的个性化每日肯定语。",
        },
    ]

    try:
        result = await zhipu_chat(messages, temperature=0.8, max_tokens=2048)
        if result is None:
            logger.warning("Affirmation generation returned None from ZhipuAI")
            return _fallback_affirmation(user_stats)
        return result
    except Exception as e:
        logger.error(f"Affirmation generation failed: {e}")
        return _fallback_affirmation(user_stats)


def _format_stats(stats: dict) -> str:
    """Format user stats into a readable summary for the AI prompt."""
    lines = []
    if stats.get("total_days") is not None:
        lines.append(f"累计训练天数：{stats['total_days']}天")
    if stats.get("consecutive_days") is not None:
        lines.append(f"连续训练天数：{stats['consecutive_days']}天")
    if stats.get("recent_training_types"):
        types_str = "、".join(stats["recent_training_types"])
        lines.append(f"近期训练类型：{types_str}")
    if stats.get("average_score") is not None:
        lines.append(f"近期平均评分：{stats['average_score']}分")
    if stats.get("last_training_type"):
        lines.append(f"最近一次训练：{stats['last_training_type']}")
    if stats.get("top_skill"):
        lines.append(f"最强技能：{stats['top_skill']}")
    if not lines:
        lines.append("新用户，暂无训练数据")
    return "\n".join(lines)


def _fallback_affirmation(user_stats: dict) -> dict:
    """Return a fallback affirmation when AI service is unavailable."""
    total_days = user_stats.get("total_days", 0)
    consecutive = user_stats.get("consecutive_days", 0)

    if total_days == 0:
        affirmation = "今天迈出第一步，就是给未来的自己最好的礼物。"
        focus_tip = "开始感官觉察基础练习"
    elif consecutive >= 7:
        affirmation = "连续七天的练习已经在重塑你的神经通路，你正在成为你想成为的人。"
        focus_tip = "今天练习一次换框技术"
    elif total_days >= 30:
        affirmation = "一个月前和今天之间，隔着的不是时间，而是你每天的觉察和选择。"
        focus_tip = "回顾进步，感受成长的力量"
    else:
        affirmation = "你追寻改变的每一天，都在给你的内在地图中绘制新的坐标。"
        focus_tip = "留意今天的一个自动化反应"

    return {
        "affirmation": affirmation,
        "focus_tip": focus_tip,
        "nlp_quote": {
            "text": "地图不是疆域。我们每个人都在用自己的内在地图导航世界，而这张地图可以重新绘制。",
            "attribution": "NLP核心前提预设",
        },
        "mini_challenge": {
            "title": "感恩觉察三分钟",
            "description": (
                "今天找一个安静的时刻，闭上眼睛，"
                "在脑海中浮现今天发生过的一个让你温暖或感激的瞬间。"
                "详细地看到那个画面的颜色、听到当时的声音、感受当时的身体感觉。"
                "让这个美好的感受在你身体中停留1分钟。"
            ),
            "duration_hint": "3分钟",
        },
    }
