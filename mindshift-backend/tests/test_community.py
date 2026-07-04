from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_post(auth_headers: dict, async_client: AsyncClient):
    """POST /community/posts creates a post and returns 201."""
    response = await async_client.post(
        "/api/v1/community/posts",
        json={"content": "Hello community!", "topic_tags": ["nlp", "practice"]},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["content"] == "Hello community!"
    assert data["topic_tags"] == ["nlp", "practice"]


@pytest.mark.asyncio
async def test_list_posts(auth_headers: dict, async_client: AsyncClient):
    """GET /community/posts returns posts list."""
    # Create a post first
    await async_client.post(
        "/api/v1/community/posts",
        json={"content": "Post for listing test"},
        headers=auth_headers,
    )

    response = await async_client.get("/api/v1/community/posts", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_like_post(auth_headers: dict, async_client: AsyncClient):
    """POST /community/posts/{id}/like increments likes."""
    # Create a post
    create_res = await async_client.post(
        "/api/v1/community/posts",
        json={"content": "Like me!"},
        headers=auth_headers,
    )
    post_id = create_res.json()["id"]

    # Like the post
    response = await async_client.post(
        f"/api/v1/community/posts/{post_id}/like",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["likes_count"] >= 1


@pytest.mark.asyncio
async def test_checkin(auth_headers: dict, async_client: AsyncClient):
    """POST /community/checkin creates a new checkin."""
    response = await async_client.post(
        "/api/v1/community/checkin",
        json={"mood": "happy", "note": "Great day!"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "checked_in"
    assert data["streak_count"] >= 1


@pytest.mark.asyncio
async def test_checkin_status(auth_headers: dict, async_client: AsyncClient):
    """GET /community/checkin/status returns today's status."""
    # First check in
    await async_client.post(
        "/api/v1/community/checkin",
        json={"mood": "excited"},
        headers=auth_headers,
    )

    response = await async_client.get(
        "/api/v1/community/checkin/status", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["checked_in"] is True
    assert data["streak_count"] >= 1


@pytest.mark.asyncio
async def test_checkin_duplicate(auth_headers: dict, async_client: AsyncClient):
    """POST /community/checkin twice returns already_checked_in status (idempotent)."""
    # First checkin
    await async_client.post(
        "/api/v1/community/checkin",
        json={"mood": "good"},
        headers=auth_headers,
    )

    # Second checkin (same day) should be idempotent
    response = await async_client.post(
        "/api/v1/community/checkin",
        json={"mood": "tired"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "already_checked_in"
