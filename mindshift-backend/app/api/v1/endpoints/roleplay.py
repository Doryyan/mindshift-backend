from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.roleplay import RpDialogueSession, RpScenario
from app.models.user import User
from app.schemas.roleplay import (
    DialogueChatRequest,
    DialogueStartRequest,
    ScenarioDetail,
    ScenarioListItem,
)
from app.services.membership.gate import get_user_membership_level
from app.services.nlp.dialogue_manager import (
    evaluate_dialogue,
    get_next_dialogue_message,
)

router = APIRouter(prefix="/roleplay", tags=["roleplay"])


@router.get("/scenarios", response_model=list[ScenarioListItem])
async def list_scenarios(
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(RpScenario)
    if category:
        query = query.where(RpScenario.category == category)
    result = await db.execute(query)
    scenarios = result.scalars().all()

    # Filter premium scenarios for free users
    user_level = await get_user_membership_level(current_user.id)
    if user_level == "free":
        scenarios = [s for s in scenarios if not s.is_premium]

    return scenarios


@router.get("/scenarios/{scenario_id}", response_model=ScenarioDetail)
async def get_scenario(
    scenario_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(RpScenario).where(RpScenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    if scenario.is_premium:
        user_level = await get_user_membership_level(current_user.id)
        if user_level == "free":
            raise HTTPException(
                status_code=403,
                detail="This scenario requires a paid membership",
            )

    return scenario


@router.post("/dialogue/start")
async def start_dialogue(
    data: DialogueStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(RpScenario).where(RpScenario.id == data.scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    initial_messages = []
    if scenario.opening_message:
        initial_messages.append({
            "role": "assistant",
            "content": scenario.opening_message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    session = RpDialogueSession(
        user_id=current_user.id,
        scenario_id=scenario.id,
        status="active",
        messages=initial_messages,
    )
    db.add(session)
    await db.flush()

    return {
        "id": session.id,
        "scenario_id": session.scenario_id,
        "status": session.status,
        "messages": session.messages,
        "started_at": session.started_at.isoformat(),
    }


@router.post("/dialogue/{session_id}/chat")
async def dialogue_chat(
    session_id: str,
    data: DialogueChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(RpDialogueSession).where(RpDialogueSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your session")
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Session is not active")

    messages = session.messages if isinstance(session.messages, list) else []
    messages.append({
        "role": "user",
        "content": data.message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    ai_response = await get_next_dialogue_message(messages, session.scenario_id)
    if ai_response:
        messages.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    session.messages = messages
    await db.flush()

    return {
        "session_id": session.id,
        "status": session.status,
        "messages": messages,
        "latest_response": ai_response,
    }


@router.post("/dialogue/{session_id}/end")
async def end_dialogue(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(RpDialogueSession).where(RpDialogueSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your session")

    messages = session.messages if isinstance(session.messages, list) else []
    nlp_score = await evaluate_dialogue(messages)

    session.status = "completed"
    session.nlp_score = nlp_score
    session.completed_at = datetime.now(timezone.utc)
    await db.flush()

    return {
        "session_id": session.id,
        "status": session.status,
        "nlp_score": nlp_score,
        "messages": messages,
        "completed_at": session.completed_at.isoformat(),
    }


@router.get("/dialogue/{session_id}/history")
async def dialogue_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(RpDialogueSession).where(RpDialogueSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your session")

    return {
        "id": session.id,
        "scenario_id": session.scenario_id,
        "status": session.status,
        "messages": session.messages,
        "nlp_score": session.nlp_score,
        "started_at": session.started_at.isoformat(),
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
    }
