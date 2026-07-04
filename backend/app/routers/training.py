from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from app.database import get_db
from app.models.training import TrainingSession
from app.models.user import User
from app.utils.security import get_current_user
from typing import Optional

router = APIRouter(prefix="/api/v1/training", tags=["Training"])

class TrainingRequest(BaseModel):
    type: str  # sensory/belief/emotion/meditation
    input: str
    title: Optional[str] = None

class TrainingResponse(BaseModel):
    id: str
    input: str
    result: str
    score: Optional[int]
    created_at: str

@router.post("")
async def submit_training(
    req: TrainingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Call AI for analysis
    analysis = await call_ai_analysis(req.type, req.input)
    
    session = TrainingSession(
        user_id=user.id, type=req.type, title=req.title,
        input=req.input, result=analysis, score=80,
    )
    db.add(session)
    user.xp += 20
    await db.flush()
    return {
        "id": session.id, "input": session.input, "result": session.result,
        "score": session.score, "created_at": session.created_at.isoformat(),
    }

@router.get("/sessions")
async def list_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(TrainingSession).where(
        TrainingSession.user_id == user.id
    ).order_by(desc(TrainingSession.created_at)).limit(50))
    return r.scalars().all()

async def call_ai_analysis(training_type: str, input_text: str) -> str:
    """Call AI for training analysis."""
    from app.config import settings
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.AI_API_KEY, base_url=settings.AI_BASE_URL)
        
        prompts = {
            "sensory": "你是NLP教练，分析用户描述的感官体验，指出其中视觉/听觉/感觉的细节，给出提升觉察力的具体建议。",
            "belief": "你是NLP教练，分析用户陈述中的限制性信念，用换框技术和次感元技术给出信念转变方案。",
            "emotion": "你是NLP教练，分析用户的情绪状态，用NLP状态管理和中断模式给出情绪调节策略。",
            "meditation": "你是NLP教练，分析用户的冥想体验，用NLP技巧给出深化练习的指导。",
        }
        system_prompt = prompts.get(training_type, "你是NLP教练，分析并给出专业建议。")
        
        resp = await client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except:
        return f"""## NLP教练分析

感谢你的分享。以下是针对你输入内容的分析：

**觉察要点**：你的描述中展现了一些思维模式，值得进一步探索。

**建议方向**：
1. 尝试从多个感官角度重新体验这个情境
2. 识别其中可能存在的惯性反应模式
3. 用换框技术寻找新的理解方式

**行动建议**：建议你在接下来48小时内，刻意应用上述方法，并记录变化。"""
