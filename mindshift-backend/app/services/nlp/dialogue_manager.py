from __future__ import annotations

import json

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.roleplay import RpScenario
from app.services.ai.zhipuai_service import (
    DIALOGUE_EVALUATION_PROMPT,
    ROLEPLAY_DIALOGUE_PROMPT,
    zhipu_chat,
)


async def get_next_dialogue_message(
    messages: list[dict], scenario_id: str
) -> str | None:
    """Get AI response for the dialogue session."""
    scenario_context = "NLP训练对话场景"
    if scenario_id:
        async with async_session_factory() as db:
            result = await db.execute(
                select(RpScenario).where(RpScenario.id == scenario_id)
            )
            scenario = result.scalar_one_or_none()
            if scenario:
                scenario_context = (
                    f"场景：{scenario.title}\n"
                    f"描述：{scenario.description or ''}\n"
                    f"角色提示：{scenario.role_prompt or ''}"
                )

    # Format dialogue history
    history_lines = []
    for msg in messages[-10:]:  # Last 10 messages for context
        role = "用户" if msg["role"] == "user" else "角色"
        history_lines.append(f"{role}：{msg['content']}")
    dialogue_history = "\n".join(history_lines)

    prompt = ROLEPLAY_DIALOGUE_PROMPT.format(
        scenario_context=scenario_context,
        dialogue_history=dialogue_history,
    )

    chat_messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "请继续对话"},
    ]

    try:
        result = await zhipu_chat(chat_messages, temperature=0.8, max_tokens=512)
        if result and "raw_response" in result:
            return result["raw_response"]
        return None
    except Exception as e:
        logger.error(f"Dialogue response generation failed: {e}")
        return "我理解你的意思。让我们继续探讨这个问题。你能分享一下你的想法吗？"


async def evaluate_dialogue(messages: list[dict]) -> dict:
    """Evaluate a completed dialogue session."""
    if not messages:
        return {"overall_score": 0, "nlp_technique_scores": {}, "feedback": ""}

    # Extract only user messages for evaluation
    user_messages = [m for m in messages if m.get("role") == "user"]
    conversation_text = "\n".join(
        [f"{i+1}. {m['content']}" for i, m in enumerate(user_messages)]
    )

    eval_messages = [
        {"role": "system", "content": DIALOGUE_EVALUATION_PROMPT},
        {"role": "user", "content": f"请评估以下对话：\n{conversation_text[:3000]}"},
    ]

    try:
        result = await zhipu_chat(eval_messages, temperature=0.3)
        if result:
            return result
    except Exception as e:
        logger.error(f"Dialogue evaluation failed: {e}")

    return {
        "overall_score": 75,
        "nlp_technique_scores": {},
        "feedback": "Evaluation service temporarily unavailable",
        "highlights": [],
        "improvements": [],
    }
