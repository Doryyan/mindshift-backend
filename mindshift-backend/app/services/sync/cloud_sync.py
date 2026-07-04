from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.training import NlpTrainingRecord
from app.models.roleplay import RpDialogueSession


SYNC_DATA_TYPES = ["training_records", "dialogue_sessions", "user_preferences"]


async def prepare_sync_manifest(
    user_id: str,
    db: AsyncSession,
) -> dict[str, Any]:
    """
    Prepare a sync manifest listing all syncable data items with their
    last-modified timestamps. The client compares this manifest against its
    local state to determine what needs to be pushed or pulled.

    Returns a dict keyed by data_type, each containing item_id -> timestamp.
    """
    manifest: dict[str, dict[str, str]] = {}

    # --- Training Records ---
    result = await db.execute(
        select(NlpTrainingRecord.id, NlpTrainingRecord.created_at).where(
            NlpTrainingRecord.user_id == user_id
        )
    )
    records = result.all()
    manifest["training_records"] = {
        row[0]: row[1].isoformat() for row in records
    }

    # --- Dialogue Sessions ---
    result = await db.execute(
        select(RpDialogueSession.id, RpDialogueSession.started_at).where(
            RpDialogueSession.user_id == user_id
        )
    )
    sessions = result.all()
    manifest["dialogue_sessions"] = {
        row[0]: row[1].isoformat() for row in sessions
    }

    # --- User Preferences (single item, keyed by "preferences") ---
    from app.models.user import User

    result = await db.execute(select(User.preferences, User.updated_at).where(User.id == user_id))
    user_row = result.one_or_none()
    if user_row and user_row[0] is not None:
        manifest["user_preferences"] = {
            "preferences": user_row[1].isoformat() if user_row[1] else ""
        }

    return manifest


def resolve_conflict(
    local_data: dict[str, Any],
    server_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Resolve conflicts between local and server data using
    last-write-wins strategy based on the 'updated_at' timestamp.

    Both local_data and server_data are expected to contain an 'updated_at'
    field with an ISO 8601 datetime string.

    Returns the winning data dict. If server_data wins, the caller should
    notify the user that their local changes were overwritten.
    """
    local_ts = _parse_timestamp(local_data.get("updated_at", ""))
    server_ts = _parse_timestamp(server_data.get("updated_at", ""))

    # If both have the same timestamp, server wins by default
    if local_ts is None and server_ts is None:
        return server_data
    if local_ts is None:
        return server_data
    if server_ts is None:
        return local_data

    # Last-write-wins: compare timestamps
    return server_data if server_ts >= local_ts else local_data


def _parse_timestamp(ts_str: str) -> datetime | None:
    """Parse ISO 8601 timestamp string, returning None on failure."""
    if not ts_str:
        return None
    try:
        dt = datetime.fromisoformat(ts_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def generate_conflict_notification(
    data_type: str,
    item_id: str,
    resolution: str,
) -> dict[str, str]:
    """
    Generate a user-facing notification message for conflict resolution.
    Sensitive data (belief diaries, roleplay dialogues) are already
    AES-256 encrypted client-side, so sync only transfers encrypted blobs.
    """
    messages = {
        "server_won": f"同步冲突已解决：{data_type} '{item_id}' 已更新为服务器版本。",
        "local_won": f"同步冲突已解决：{data_type} '{item_id}' 保留了您的本地版本。",
    }
    return {
        "type": "conflict_resolution",
        "data_type": data_type,
        "item_id": item_id,
        "resolution": resolution,
        "message": messages.get(resolution, ""),
    }
