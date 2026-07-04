from __future__ import annotations

from loguru import logger

from app.services.ai.zhipuai_service import zhipu_chat

BELIEF_MINING_PROMPT = """你是一位资深的NLP（神经语言程序学）信念分析师。请对用户的输入进行三步信念分析，并以JSON格式返回结果。

分析步骤：

**第一步：识别限制性信念**
从用户的描述中识别表面问题，然后找到语言之下隐藏的限制性信念。限制性信念通常以以下形式出现：
- 普遍性陈述："我永远...""我总是...""从来没有人..."
- 等价信念："如果...就意味着..."
- 因果信念："因为...所以我不能..."

**第二步：分析信念结构**
对每个限制性信念进行结构分析：
- supporting_evidence: 用户用来支持这个信念的"证据"（通常是过去某个事件的过度泛化）
- emotional_payoff: 持有这个信念给用户带来的情绪回报（如：不用承担责任、获得同情、避免风险）
- cost: 这个信念带来的真实代价（机会损失、关系损耗、心理健康成本）

**第三步：引导信念转化**
为每个限制性信念提供转化引导：
- reframe_perspective: 一个重新框架的视角（用新的方式看待同一个事实）
- challenge_questions: 2个挑战性提问，帮助用户松动旧信念
- new_belief_seed: 一个新的、更有力量的替代信念种子
- transformation_anchor: 一个具体的身体锚点或动作，帮助用户在日常生活中激活新信念

请严格按照以下JSON格式返回：
{
  "surface_problem": "用户呈现的表面问题",
  "limiting_beliefs": [
    {
      "belief": "限制性信念陈述",
      "category": "能力/身份/关系/时间/资源",
      "intensity": 8,
      "origin_hint": "可能源自..."
    }
  ],
  "belief_structure": {
    "primary_belief": "最核心的限制性信念",
    "supporting_evidence": ["证据1", "证据2"],
    "emotional_payoff": "持有该信念的隐性回报",
    "cost": "该信念的实际代价",
    "belief_chain": "完整信念链条的逐层分析"
  },
  "transformation_guide": {
    "reframe_perspectives": ["重新框架视角1", "重新框架视角2"],
    "challenge_questions": ["挑战性问题1", "挑战性问题2", "挑战性问题3"],
    "new_belief_seed": "可以替代旧信念的新信念种子",
    "transformation_anchor": "身体锚点或行动建议",
    "daily_practice": "日常练习建议"
  }
}"""


async def mine_beliefs(user_input: str) -> dict | None:
    """Analyze user input for limiting beliefs using NLP belief mining.

    Args:
        user_input: The user's description of their situation or concern

    Returns:
        Dict with surface_problem, limiting_beliefs, belief_structure, transformation_guide
        or None if analysis fails
    """
    if not user_input or len(user_input.strip()) < 10:
        logger.warning("Belief mining input too short")
        return None

    messages = [
        {"role": "system", "content": BELIEF_MINING_PROMPT},
        {
            "role": "user",
            "content": f"请分析以下用户输入中的限制性信念：\n\n{user_input}",
        },
    ]

    try:
        result = await zhipu_chat(messages, temperature=0.4, max_tokens=4096)
        if result is None:
            logger.warning("Belief mining returned None from ZhipuAI")
            return _fallback_response(user_input)
        return result
    except Exception as e:
        logger.error(f"Belief mining failed: {e}")
        return _fallback_response(user_input)


def _fallback_response(user_input: str) -> dict:
    """Return a fallback response when the AI service is unavailable."""
    return {
        "surface_problem": user_input[:100],
        "limiting_beliefs": [
            {
                "belief": "暂时无法完成深度分析",
                "category": "未知",
                "intensity": 5,
                "origin_hint": "请在服务恢复后重试",
            }
        ],
        "belief_structure": {
            "primary_belief": "分析服务暂时不可用",
            "supporting_evidence": [],
            "emotional_payoff": "",
            "cost": "",
            "belief_chain": "",
        },
        "transformation_guide": {
            "reframe_perspectives": ["请在稍后重试以获得完整分析"],
            "challenge_questions": [],
            "new_belief_seed": "保持耐心，成长需要时间",
            "transformation_anchor": "深呼吸三次，等待服务恢复",
            "daily_practice": "在此期间，可以尝试自我提问：'如果这个想法不是真的，我的生活会有什么不同？'",
        },
    }
