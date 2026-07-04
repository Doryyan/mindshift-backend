from __future__ import annotations

from loguru import logger

from app.services.ai.zhipuai_service import zhipu_chat

DREAM_ANALYSIS_PROMPT = """你是一位NLP梦境分析师，擅长从NLP次感元（Submodalities）和表象系统的角度分析梦境。

请从以下NLP视角分析用户描述的梦境：

分析维度：

1. **主导感官通道（Dominant Modalities）**
识别梦境中哪个感官通道最为活跃：视觉（光影、颜色、场景清晰度）、听觉（对话、声音、音乐）、
触觉/身体感（质感、温度、疼痛、身体动作）、嗅觉/味觉。

2. **象征元素解读（Symbolic Elements）**
从NLP角度看，梦境中的每个元素都是次感元编码的产物。分析关键象征元素：
- 人物角色的次感元特征（大小、位置、距离、清晰度）
- 关键物体/场景的感官属性
- 情绪色调（从冷到暖、从亮到暗）

3. **情绪签名（Emotional Signature）**
分析梦境中情绪的次感元结构：
- 核心情绪是什么？
- 这种情绪在身体中的感觉（在哪个部位？什么质感？什么温度？）
- 梦中的情绪与清醒时的什么情境有关联？

4. **转化建议（Transformation Suggestion）**
基于NLP技术，为梦者的成长提供方向：
- 如果梦境中某个元素可以调整次感元（变大变小、走近走远、清晰模糊），哪个调整可能改变整个梦的情绪基调？
- 在清醒状态下如何用NLP技术处理梦中的情绪？
- 有什么具体的心锚或练习建议？

请严格按照以下JSON格式返回：
{
  "dominant_modalities": [
    {
      "channel": "视觉/听觉/触觉/嗅觉/味觉",
      "intensity": 8,
      "description": "该通道在梦中的具体表现"
    }
  ],
  "symbolic_elements": [
    {
      "element": "梦中的关键元素（人物/物品/场景）",
      "nlp_interpretation": "从NLP次感元角度的解读",
      "submodality_features": {
        "size": "大/中/小",
        "distance": "近/中/远",
        "clarity": "清晰/模糊",
        "color": "色彩特征",
        "movement": "静止/缓慢/快速"
      },
      "potential_meaning": "该元素可能象征的心理含义"
    }
  ],
  "emotional_signature": {
    "primary_emotion": "核心情绪",
    "body_location": "情绪在身体中的位置",
    "submodality_structure": "该情绪的次感元结构（如：紧绷感、重量感、温度等）",
    "waking_life_connection": "与清醒生活的可能关联"
  },
  "transformation_suggestion": {
    "submodality_intervention": "次感元干预建议（调整梦境的某个感官属性）",
    "nlp_practice": "可执行的NLP练习",
    "anchor_suggestion": "建议安装的心锚",
    "reflection_questions": ["反思问题1", "反思问题2", "反思问题3"]
  }
}"""


async def analyze_dream(dream_text: str) -> dict | None:
    """Analyze a dream from NLP submodality perspective.

    Args:
        dream_text: The dream description text (at least 20 characters)

    Returns:
        Dict with dominant_modalities, symbolic_elements, emotional_signature,
        transformation_suggestion, or None if analysis fails
    """
    if not dream_text or len(dream_text.strip()) < 20:
        logger.warning("Dream text too short for analysis")
        return None

    messages = [
        {"role": "system", "content": DREAM_ANALYSIS_PROMPT},
        {
            "role": "user",
            "content": f"请从NLP次感元角度分析以下梦境：\n\n{dream_text}",
        },
    ]

    try:
        result = await zhipu_chat(messages, temperature=0.5, max_tokens=4096)
        if result is None:
            logger.warning("Dream analysis returned None from ZhipuAI")
            return _fallback_dream_analysis(dream_text)
        return result
    except Exception as e:
        logger.error(f"Dream analysis failed: {e}")
        return _fallback_dream_analysis(dream_text)


def _fallback_dream_analysis(dream_text: str) -> dict:
    """Return a fallback analysis when AI service is unavailable."""
    return {
        "dominant_modalities": [
            {
                "channel": "视觉",
                "intensity": 7,
                "description": "梦境以视觉体验为主，画面具有较强的感官印象",
            }
        ],
        "symbolic_elements": [
            {
                "element": "梦境整体氛围",
                "nlp_interpretation": "梦境是潜意识用次感元编码呈现的情绪信息",
                "submodality_features": {
                    "size": "中",
                    "distance": "中",
                    "clarity": "模糊",
                    "color": "依梦境描述而定",
                    "movement": "依梦境描述而定",
                },
                "potential_meaning": "梦境的象征意义需要根据具体元素进一步分析",
            }
        ],
        "emotional_signature": {
            "primary_emotion": "根据梦境描述推断",
            "body_location": "胸腔区域",
            "submodality_structure": "可能包含紧绷感或重量感",
            "waking_life_connection": "梦境情绪通常与近期经历或潜在关注点相关",
        },
        "transformation_suggestion": {
            "submodality_intervention": (
                "尝试在清醒状态闭上眼睛，回到梦中最让你印象深刻的一个画面。"
                "将该画面推远，缩小到手掌大小，将颜色调成柔和的暖色调。"
                "观察你的情绪变化。"
            ),
            "nlp_practice": (
                "记录一周的梦境日志，重点关注每个梦中的感官细节：你看到了什么颜色？"
                "听到了什么声音？感受到了什么质感？这将帮助你建立对内在表征系统的觉察。"
            ),
            "anchor_suggestion": "在睡前深呼吸三次并轻拍心口，安装一个'安全入睡'心锚",
            "reflection_questions": [
                "如果梦中的主要情绪可以用一种颜色来形容，那是什么颜色？",
                "梦中哪个画面如果改变大小或距离，会让整个梦的情绪发生最大变化？",
                "醒来后，你身体哪个部位仍然残留着梦中的感觉？",
            ],
        },
    }
