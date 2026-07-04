from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_summary(auth_headers: dict, async_client: AsyncClient):
    """GET /progress/summary returns summary data."""
    response = await async_client.get("/api/v1/progress/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_trainings" in data
    assert "total_roleplays" in data
    assert "average_score" in data
    assert "streak_days" in data
    assert "user_stage" in data


@pytest.mark.asyncio
async def test_get_radar(auth_headers: dict, async_client: AsyncClient):
    """GET /progress/radar returns radar chart data."""
    response = await async_client.get("/api/v1/progress/radar", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "sensory_acuity" in data
    assert "rapport_building" in data
    assert "belief_transformation" in data
    assert "submodality_mastery" in data
    assert "language_pattern" in data
    assert "state_management" in data
    assert "anchoring_skill" in data
    assert "reframing_skill" in data
