from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models.roleplay import Scenario, RoleplaySession
from app.models.user import User
from app.utils.security import get_current_user
import json
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/roleplay", tags=["Roleplay"])

class DialogueRequest(BaseModel):
    scenario_id: str
    message: str
    session_id: Optional[str] = None

class DialogueResponse(BaseModel):
    reply: str
    session_id: str
    messages: list = []

@router.get("/scenarios")
async def list_scenarios(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(Scenario).order_by(Scenario.sort_order, Scenario.created_at.desc())
    if category: q = q.where(Scenario.category == category)
    result = await db.execute(q)
    return result.scalars().all()

@router.get("/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Scenario).where(Scenario.id == scenario_id))
    sc = r.scalar_one_or_none()
    if not sc: raise HTTPException(404, "场景不存在")
    return sc

@router.post("/dialogue", response_model=DialogueResponse)
async def dialogue(
    req: DialogueRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get or create session
    if req.session_id:
        r = await db.execute(select(RoleplaySession).where(
            RoleplaySession.id == req.session_id, RoleplaySession.user_id == user.id
        ))
        session = r.scalar_one_or_none()
        if not session: raise HTTPException(404, "会话不存在")
    else:
        session = RoleplaySession(user_id=user.id, scenario_id=req.scenario_id, messages="[]")
        db.add(session)
        await db.flush()

    # Load existing messages
    messages = json.loads(session.messages) if session.messages else []
    # If this is a new session (no messages), return scenario opening
    if len(messages) == 0:
        r_sc = await db.execute(select(Scenario).where(Scenario.id == req.scenario_id))
        scenario = r_sc.scalar_one_or_none()
        opening = scenario.opening_message if scenario and scenario.opening_message else "你好！我是你的NLP练习教练，让我们开始吧。请描述你遇到的情况，我会引导你完成练习。"
        messages.append({"role": "assistant", "content": opening, "timestamp": datetime.now(timezone.utc).isoformat()})
        session.messages = json.dumps(messages, ensure_ascii=False)
        await db.flush()
        return DialogueResponse(reply=opening, session_id=session.id, messages=messages)
    messages.append({"role": "user", "content": req.message, "timestamp": datetime.now(timezone.utc).isoformat()})
    
    # Call AI
    ai_reply = await call_ai_dialogue(req.scenario_id, messages)
    messages.append({"role": "assistant", "content": ai_reply, "timestamp": datetime.now(timezone.utc).isoformat()})
    
    session.messages = json.dumps(messages, ensure_ascii=False)
    await db.flush()
    
    return DialogueResponse(reply=ai_reply, session_id=session.id, messages=messages)

async def call_ai_dialogue(scenario_id: str, messages: list) -> str:
    """Call ZhipuAI or configured AI for dialogue."""
    from app.config import settings
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.AI_API_KEY, base_url=settings.AI_BASE_URL)
        
        # Get scenario system prompt
        from app.database import async_session
        from app.models.roleplay import Scenario
        async with async_session() as s:
            r = await s.execute(select(Scenario).where(Scenario.id == scenario_id))
            sc = r.scalar_one_or_none()
        
        system_prompt = f"""你是一位专业的NLP（神经语言程序学）教练，正在与学员进行角色扮演练习。
场景：{sc.title if sc else 'NLP对话练习'}
角色：你扮演对话中的另一方，以NLP理论为指导进行互动。

核心要求：
1. 用NLP的感官觉察技术回应对方，指出你观察到的语言模式
2. 适时运用换框技术、米尔顿模式、次感元技术
3. 每次回应要自然、贴近真实对话场景
4. 结合对方的具体话语给出反馈，不是笼统说教
5. 每次回复80-150字，提供具体的沟通建议

你的开场白：{sc.opening_message if sc and sc.opening_message else '你好，我注意到你刚才的表达方式，让我们来一起练习更有效的沟通方式。'}
"""
        msgs = [{"role": "system", "content": system_prompt}]
        for m in messages[-10:]:  # Keep last 10 messages for context
            msgs.append({"role": m["role"], "content": m["content"]})
        
        resp = await client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=msgs,
            max_tokens=300,
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        # Fallback response without AI
        return f"""收到你的分享。从NLP的角度来看，我注意到你在沟通中展现了一些模式。

建议你尝试以下方式：
1. 先觉察自己的情绪状态，使用中断模式暂停惯性反应
2. 用换框技术重新看待当前的情境
3. 想象你期望的理想结果，反向推导所需的沟通步骤

你可以具体说说你希望在哪方面得到改善吗？"""
