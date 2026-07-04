from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.training import NlpTrainingRecord
from app.models.roleplay import RpDialogueSession
from app.models.user import User
from app.services.sync.cloud_sync import (
    SYNC_DATA_TYPES,
    prepare_sync_manifest,
    resolve_conflict,
    generate_conflict_notification,
)

router = APIRouter(prefix="/sync", tags=["sync"])


# --- Request / Response Schemas ---

class SyncItem(BaseModel):
    id: str
    data_type: str
    payload: dict[str, Any]
    updated_at: str  # ISO 8601


class PushRequest(BaseModel):
    items: list[SyncItem]

    @field_validator("items")
    @classmethod
    def check_data_types(cls, v: list[SyncItem]) -> list[SyncItem]:
        for item in v:
            if item.data_type not in SYNC_DATA_TYPES:
                raise ValueError(f"Unknown data_type: {item.data_type}")
        return v


class PullRequest(BaseModel):
    data_types: list[str]  # e.g. ["training_records", "dialogue_sessions"]

    @field_validator("data_types")
    @classmethod
    def check_data_types(cls, v: list[str]) -> list[str]:
        for dt in v:
            if dt not in SYNC_DATA_TYPES:
                raise ValueError(f"Unknown data_type: {dt}")
        return v


class SyncManifestResponse(BaseModel):
    user_id: str
    manifest: dict[str, dict[str, str]]
    server_time: str


class PushResponse(BaseModel):
    saved: int
    conflicts: list[dict[str, str]]
    notifications: list[dict[str, str]]


class PullResponse(BaseModel):
    items: list[SyncItem]
    server_time: str


# --- Endpoints ---

@router.get("/manifest", response_model=SyncManifestResponse)
async def get_sync_manifest(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return the list of all syncable items for the current user,
    with their last-modified timestamps. The client uses this to
    determine which data needs to be pushed or pulled.
    """
    from datetime import datetime, timezone

    manifest = await prepare_sync_manifest(current_user.id, db)
    return SyncManifestResponse(
        user_id=current_user.id,
        manifest=manifest,
        server_time=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/push", response_model=PushResponse)
async def push_sync_data(
    request: PushRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Push encrypted local data to the server. Each item is compared
    against the server version using last-write-wins conflict resolution.
    """
    saved = 0
    conflicts: list[dict[str, str]] = []
    notifications: list[dict[str, str]] = []

    for item in request.items:
        existing = await _fetch_server_item(db, current_user.id, item.data_type, item.id)
        if existing:
            # Conflict resolution
            server_version = {
                "updated_at": existing.get("updated_at", ""),
            }
            local_version = {
                "updated_at": item.updated_at,
            }
            winner = resolve_conflict(local_version, server_version)
            if winner is local_version:
                # Local data wins - update server
                await _upsert_item(db, current_user.id, item)
                saved += 1
                notification = generate_conflict_notification(
                    item.data_type, item.id, "local_won"
                )
                notifications.append(notification)
            else:
                # Server data wins
                conflicts.append({
                    "id": item.id,
                    "data_type": item.data_type,
                    "resolution": "server_won",
                })
                notification = generate_conflict_notification(
                    item.data_type, item.id, "server_won"
                )
                notifications.append(notification)
        else:
            # No conflict - simply save
            await _upsert_item(db, current_user.id, item)
            saved += 1

    await db.flush()
    return PushResponse(
        saved=saved,
        conflicts=conflicts,
        notifications=notifications,
    )


@router.get("/pull", response_model=PullResponse)
async def pull_sync_data(
    data_types: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Pull server-side data that the client needs. If data_types query param
    is provided (comma-separated), only pull those types. Otherwise, pull
    all syncable data.
    """
    from datetime import datetime, timezone

    if data_types:
        types_to_pull = [dt.strip() for dt in data_types.split(",")]
        # Validate data types
        for dt in types_to_pull:
            if dt not in SYNC_DATA_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unknown data_type: {dt}. Valid types: {SYNC_DATA_TYPES}",
                )
    else:
        types_to_pull = list(SYNC_DATA_TYPES)

    items: list[SyncItem] = []

    if "training_records" in types_to_pull:
        result = await db.execute(
            select(NlpTrainingRecord).where(
                NlpTrainingRecord.user_id == current_user.id
            )
        )
        records = result.scalars().all()
        for record in records:
            items.append(
                SyncItem(
                    id=record.id,
                    data_type="training_records",
                    payload={
                        "training_type": record.training_type,
                        "input_data": record.input_data,
                        "ai_result": record.ai_result,
                        "overall_score": record.overall_score,
                        "time_spent_seconds": record.time_spent_seconds,
                    },
                    updated_at=record.created_at.isoformat(),
                )
            )

    if "dialogue_sessions" in types_to_pull:
        result = await db.execute(
            select(RpDialogueSession).where(
                RpDialogueSession.user_id == current_user.id
            )
        )
        sessions = result.scalars().all()
        for session in sessions:
            items.append(
                SyncItem(
                    id=session.id,
                    data_type="dialogue_sessions",
                    payload={
                        "scenario_id": session.scenario_id,
                        "status": session.status,
                        "messages": session.messages,
                        "nlp_score": session.nlp_score,
                        "started_at": session.started_at.isoformat(),
                        "completed_at": session.completed_at.isoformat()
                        if session.completed_at
                        else None,
                    },
                    updated_at=session.started_at.isoformat(),
                )
            )

    if "user_preferences" in types_to_pull:
        result = await db.execute(select(User).where(User.id == current_user.id))
        user = result.scalar_one_or_none()
        if user and user.preferences:
            items.append(
                SyncItem(
                    id="preferences",
                    data_type="user_preferences",
                    payload={"preferences": user.preferences},
                    updated_at=user.updated_at.isoformat()
                    if user.updated_at
                    else "",
                )
            )

    return PullResponse(
        items=items,
        server_time=datetime.now(timezone.utc).isoformat(),
    )


# --- Internal Helpers ---

async def _fetch_server_item(
    db: AsyncSession,
    user_id: str,
    data_type: str,
    item_id: str,
) -> dict[str, Any] | None:
    """Fetch a single item from the server for conflict comparison."""
    if data_type == "training_records":
        result = await db.execute(
            select(NlpTrainingRecord).where(
                NlpTrainingRecord.id == item_id,
                NlpTrainingRecord.user_id == user_id,
            )
        )
        record = result.scalar_one_or_none()
        if record:
            return {
                "updated_at": record.created_at.isoformat(),
            }
    elif data_type == "dialogue_sessions":
        result = await db.execute(
            select(RpDialogueSession).where(
                RpDialogueSession.id == item_id,
                RpDialogueSession.user_id == user_id,
            )
        )
        session = result.scalar_one_or_none()
        if session:
            return {
                "updated_at": session.started_at.isoformat(),
            }
    elif data_type == "user_preferences":
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user and user.preferences is not None:
            return {
                "updated_at": user.updated_at.isoformat() if user.updated_at else "",
            }
    return None


async def _upsert_item(
    db: AsyncSession,
    user_id: str,
    item: SyncItem,
) -> None:
    """Insert or update a sync item in the database."""
    if item.data_type == "training_records":
        record = NlpTrainingRecord(
            id=item.id,
            user_id=user_id,
            training_type=item.payload.get("training_type", ""),
            input_data=item.payload.get("input_data", {}),
            ai_result=item.payload.get("ai_result"),
            overall_score=item.payload.get("overall_score"),
            time_spent_seconds=item.payload.get("time_spent_seconds", 0),
        )
        await db.merge(record)
    elif item.data_type == "dialogue_sessions":
        session = RpDialogueSession(
            id=item.id,
            user_id=user_id,
            scenario_id=item.payload.get("scenario_id", ""),
            status=item.payload.get("status", "active"),
            messages=item.payload.get("messages", []),
            nlp_score=item.payload.get("nlp_score"),
        )
        await db.merge(session)
    elif item.data_type == "user_preferences":
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.preferences = item.payload.get("preferences", {})
            await db.merge(user)
