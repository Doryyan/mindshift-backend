from __future__ import annotations

from loguru import logger

from app.services.ai.zhipuai_service import zhipu_chat

GUIDED_MEDITATION_PROMPT = """你是一位资深的NLP冥想引导师，擅长将NLP核心技术与正念冥想相结合，为练习者创造个性化、有深度的引导冥想体验。

请根据用户当前的情绪状态和NLP聚焦领域，生成一份个性化的NLP引导冥想脚本。

冥想设计要求：
1. 以一个温和的身体觉察引导开始（锚定当下）
2. 用次感元技术引导用户调整内在画面：从当前的负面状态画面逐步转化
3. 融入信念转化元素：在冥想的高阶阶段植入新的资源性信念
4. 使用感官语言（视觉、听觉、触觉）丰富冥想体验
5. 设置一个心锚：在冥想结束时用一个呼吸或身体动作锚定积极状态
6. 每一步都配有具体的引导语和持续时间建议

NLP冥想关键要素：
- 表象系统切换：引导用户在不同感官通道之间切换
- 次感元调节：帮助用户调整内在表征的大小、距离、亮度、音量等
- 心锚安装：在最佳状态时设置可触发的锚点
- 时间线应用：引导用户在时间线上找到资源状态
- 知觉位置：让练习者从不同视角体验同一情境

请严格按照以下JSON格式返回：
{
  "title": "个性化的冥想标题（15字以内）",
  "duration_suggestion": 15,
  "focus_area": "本次冥想的NLP聚焦领域",
  "preparation": "冥想前的准备建议（坐姿、环境等）",
  "script": [
    {
      "step": 1,
      "phase": "锚定当下",
      "duration_seconds": 120,
      "guidance": "详细引导语...",
      "nlp_element": "此处运用的NLP技术说明"
    },
    {
      "step": 2,
      "phase": "次感元调整",
      "duration_seconds": 180,
      "guidance": "详细引导语...",
      "nlp_element": "此处运用的NLP技术说明"
    },
    {
      "step": 3,
      "phase": "信念转化",
      "duration_seconds": 180,
      "guidance": "详细引导语...",
      "nlp_element": "此处运用的NLP技术说明"
    },
    {
      "step": 4,
      "phase": "资源整合",
      "duration_seconds": 120,
      "guidance": "详细引导语...",
      "nlp_element": "此处运用的NLP技术说明"
    },
    {
      "step": 5,
      "phase": "心锚安装与结束",
      "duration_seconds": 120,
      "guidance": "详细引导语...",
      "nlp_element": "此处运用的NLP技术说明"
    }
  ],
  "anchor_phrase": "提醒语（10字以内，作为当天的锚点短句）",
  "post_meditation_note": "冥想后的延续练习建议"
}"""


async def generate_meditation(state: str, focus: str) -> dict | None:
    """Generate a personalized NLP guided meditation script.

    Args:
        state: User's current emotional state (e.g., "焦虑", "疲惫", "迷茫")
        focus: NLP focus area (e.g., "信念转化", "次感元调整", "心锚安装")

    Returns:
        Dict with title, duration_suggestion, script, anchor_phrase
        or None if generation fails
    """
    if not state or not focus:
        logger.warning("Meditation generation requires both state and focus")
        return None

    valid_focuses = [
        "信念转化", "次感元调整", "心锚安装", "感官觉察",
        "换框练习", "状态管理", "资源整合", "内在小孩对话",
        "未来模拟", "时间线疗愈",
    ]

    if focus not in valid_focuses:
        logger.warning(f"Unknown focus area: {focus}, using default")
        focus = "感官觉察"

    messages = [
        {"role": "system", "content": GUIDED_MEDITATION_PROMPT},
        {
            "role": "user",
            "content": (
                f"用户当前的情绪状态：{state}\n"
                f"希望聚焦的NLP领域：{focus}\n"
                f"请生成一份适合当前状态的个性化NLP引导冥想。"
            ),
        },
    ]

    try:
        result = await zhipu_chat(messages, temperature=0.7, max_tokens=4096)
        if result is None:
            logger.warning("Meditation generation returned None from ZhipuAI")
            return _fallback_meditation(state, focus)
        return result
    except Exception as e:
        logger.error(f"Meditation generation failed: {e}")
        return _fallback_meditation(state, focus)


def _fallback_meditation(state: str, focus: str) -> dict:
    """Return a fallback meditation when AI service is unavailable."""
    return {
        "title": f"平静之海：{focus}冥想",
        "duration_suggestion": 10,
        "focus_area": focus,
        "preparation": "找一个安静舒适的地方坐下，背部挺直，双手自然放在膝盖上。",
        "script": [
            {
                "step": 1,
                "phase": "锚定当下",
                "duration_seconds": 90,
                "guidance": (
                    "闭上眼睛，将注意力带到你的呼吸上。"
                    "感受空气从鼻腔进入、经过喉咙、充满胸腔的整个过程。"
                    "不需要改变呼吸，只是观察它。"
                    "每一次呼气，让身体释放一点紧张。"
                ),
                "nlp_element": "感官觉察——通过呼吸锚定当下的身体感受",
            },
            {
                "step": 2,
                "phase": "次感元调整",
                "duration_seconds": 120,
                "guidance": (
                    "现在，在脑海中浮现一个代表你当前状态的画面。"
                    "观察它的颜色、大小、距离。"
                    "将画面推远一些，缩小到电视屏幕大小。"
                    "将颜色从锐利调成柔和。感受画面的情绪强度在减弱。"
                ),
                "nlp_element": "次感元调节——通过调整内在画面的视觉属性降低情绪强度",
            },
            {
                "step": 3,
                "phase": "信念转化",
                "duration_seconds": 120,
                "guidance": (
                    "在心中轻声重复：'我拥有改变的力量。'"
                    "留意这句话在身体中引发的感受——"
                    "也许胸口有微微的暖意，也许肩膀变得更放松。"
                    "让这个感受慢慢扩散到全身。"
                    "想象你站在未来的某一天，已经成为了你想成为的样子。"
                    "未来版本的你正在现在给你一个温暖的笑容。"
                ),
                "nlp_element": "信念植入和未来模拟——用时间线和身体感受建立新信念",
            },
            {
                "step": 4,
                "phase": "资源整合",
                "duration_seconds": 90,
                "guidance": (
                    "现在，回顾你的一生中那些让你感到自信、平静、有力量的时刻。"
                    "这些资源一直都在你体内。"
                    "让这些记忆的色彩、声音和感受在身体中重新鲜活起来。"
                    "注意到你的姿势自然变得挺直，呼吸变得更平稳。"
                ),
                "nlp_element": "资源状态调用——回溯并激活内在资源",
            },
            {
                "step": 5,
                "phase": "心锚安装与结束",
                "duration_seconds": 60,
                "guidance": (
                    "当这种良好的感受达到顶峰时，将右手轻轻放在心口。"
                    "深呼吸一次，将这种感觉与这个动作锁定在一起。"
                    "以后任何时候你需要这种感觉，只需将手放在同一个位置，深呼吸一次。"
                    "现在，慢慢将注意力带回到房间。活动一下手指和脚趾。"
                    "当你准备好了，睁开眼睛。"
                ),
                "nlp_element": "心锚安装——将积极状态与身体动作绑定",
            },
        ],
        "anchor_phrase": "平静已在心中",
        "post_meditation_note": "今天每当感到压力时，将手放在心口深呼吸，唤醒你的平静心锚。",
    }
