from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

import httpx
from loguru import logger

from app.core.config import settings

ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# Simple in-memory cache for daily affirmation requests (same user, same day)
_affirmation_cache: dict[str, dict[str, Any]] = {}


def _get_affirmation_cache_key(user_id: str, date_str: str) -> str:
    raw = f"{user_id}:{date_str}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def zhipu_chat(
    messages: list[dict[str, str]],
    model: str = "glm-4-flash",
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> dict[str, Any] | None:
    """Call ZhipuAI Chat API and return parsed JSON result."""
    headers = {
        "Authorization": f"Bearer {settings.ZHIPUAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(trust_env=False, timeout=60.0) as client:
        try:
            response = await client.post(ZHIPU_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Try to parse JSON from response
            json_start = content.find("{")
            json_end = content.rfind("}")
            if json_start != -1 and json_end != -1:
                return json.loads(content[json_start : json_end + 1])
            return {"raw_response": content}
        except httpx.HTTPStatusError as e:
            logger.error(f"ZhipuAI HTTP error: {e.response.status_code} {e.response.text}")
            return None
        except (httpx.RequestError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"ZhipuAI call failed: {e}")
            return None


async def zhipu_chat_cached(
    messages: list[dict[str, str]],
    user_id: str | None = None,
    model: str = "glm-4-flash",
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> dict[str, Any] | None:
    """Call ZhipuAI with caching for daily affirmation requests."""
    if user_id:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        cache_key = _get_affirmation_cache_key(user_id, today)

        # Check if we have a cached response for this user today
        if cache_key in _affirmation_cache:
            logger.info(f"Returning cached affirmation for user {user_id}")
            return _affirmation_cache[cache_key]

        result = await zhipu_chat(messages, model, temperature, max_tokens)
        if result is not None:
            _affirmation_cache[cache_key] = result
        return result

    return await zhipu_chat(messages, model, temperature, max_tokens)


# Enhanced evaluation prompt with streaming support flag
NLP_EVALUATION_PROMPT = """你是一位专业的NLP（神经语言程序学）教练。请评估以下训练内容，并以JSON格式返回结果。

评估维度：
1. overall_score: 0-100的综合分数
2. dimensions: 各分项维度评分
   - accuracy: 技术准确性
   - depth: 理解深度
   - application: 应用能力
   - clarity: 表达清晰度
   - creativity: 创造性
3. feedback: 总体反馈
4. suggestions: 改进建议列表
5. strengths: 表现优势列表

请严格按照以下JSON格式返回，不要添加任何其他文字：
{
  "overall_score": 85,
  "dimensions": {"accuracy": 85, "depth": 80, "application": 90, "clarity": 85, "creativity": 80},
  "feedback": "你的表现很好...",
  "suggestions": ["建议1", "建议2"],
  "strengths": ["优势1", "优势2"]
}"""


ROLEPLAY_DIALOGUE_PROMPT = """你是一位NLP训练场景中的角色扮演伙伴。请根据以下场景设定回应。

要求：
1. 保持角色一致性
2. 自然而真实地回应
3. 适度挑战用户，促进其NLP技巧运用
4. 回应应简洁有力，不超过200字
5. 始终保持支持和鼓励的态度

场景设定：{scenario_context}

对话历史：
{dialogue_history}

请回应用户的最后一条消息。"""


DIALOGUE_EVALUATION_PROMPT = """你是一位NLP教练，请评估以下角色扮演对话，并以JSON格式返回。

评估维度：
1. overall_score: 0-100的综合分数
2. nlp_technique_scores: 各项NLP技巧评分
   - rapport: 建立亲和力
   - sensory_acuity: 感官敏锐度
   - language_pattern: 语言模式
   - reframing: 重新框架能力
   - state_management: 状态管理
3. feedback: 总体反馈
4. highlights: 亮点
5. improvements: 改进建议

请严格按照以下JSON格式返回：
{
  "overall_score": 85,
  "nlp_technique_scores": {"rapport": 85, "sensory_acuity": 80, "language_pattern": 90, "reframing": 80, "state_management": 85},
  "feedback": "整体表现不错...",
  "highlights": ["亮点1", "亮点2"],
  "improvements": ["改进1", "改进2"]
}"""
