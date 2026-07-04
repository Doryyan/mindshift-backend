from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    """POST /auth/register returns 201 + token."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@test.com", "password": "Test123456", "nickname": "NewUser"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient):
    """POST /auth/register with duplicate email returns 400."""
    payload = {"email": "dup@test.com", "password": "Test123456", "nickname": "DupUser"}
    # First registration succeeds
    response1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert response1.status_code == 201
    # Second registration fails
    response2 = await async_client.post("/api/v1/auth/register", json=payload)
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    """POST /auth/login returns 200 + token."""
    # Register first
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "login@test.com", "password": "Test123456", "nickname": "LoginUser"},
    )
    # Then login
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "Test123456"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient):
    """POST /auth/login with wrong password returns 401."""
    # Register first
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpw@test.com", "password": "Test123456", "nickname": "WrongPw"},
    )
    # Login with wrong password
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpw@test.com", "password": "WrongPassword999"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(auth_headers: dict, async_client: AsyncClient):
    """GET /auth/me with valid token returns user info."""
    response = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "nickname" in data


@pytest.mark.asyncio
async def test_me_unauthenticated(async_client: AsyncClient):
    """GET /auth/me without token returns 401."""
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401
