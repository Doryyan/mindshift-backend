from __future__ import annotations

from loguru import logger

from app.services.ai.zhipuai_service import NLP_EVALUATION_PROMPT, zhipu_chat


async def evaluate_training(
    training_type: str, input_data: dict
) -> dict | None:
    """Evaluate a training input using ZhipuAI."""
    if not input_data:
        return None

    # Build the user message from input data
    input_text = input_data.get("text", input_data.get("content", str(input_data)))

    messages = [
        {"role": "system", "content": NLP_EVALUATION_PROMPT},
        {
            "role": "user",
            "content": f"训练类型：{training_type}\n训练内容：\n{input_text}",
        },
    ]

    try:
        result = await zhipu_chat(messages, temperature=0.5, max_tokens=800)
        return result
    except Exception as e:
        logger.error(f"Training evaluation failed: {e}")
        return {
            "overall_score": 70,
            "dimensions": {},
            "feedback": "Evaluation service temporarily unavailable",
            "suggestions": [],
            "strengths": [],
        }
