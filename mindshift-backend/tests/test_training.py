from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_evaluate_training(auth_headers: dict, async_client: AsyncClient):
    """POST /training/evaluate returns score, using mocked AI service."""
    mock_result = {
        "overall_score": 85,
        "dimensions": {"accuracy": 85, "depth": 80, "application": 90, "clarity": 85, "creativity": 80},
        "feedback": "Good work on the training!",
        "suggestions": ["Practice more"],
        "strengths": ["Good accuracy"],
    }

    with patch(
        "app.api.v1.endpoints.training.evaluate_training",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        response = await async_client.post(
            "/api/v1/training/evaluate",
            json={
                "training_type": "sensory",
                "input_data": {"text": "I practiced sensory acuity today"},
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["overall_score"] == 85
        assert data["ai_result"] == mock_result
        assert "id" in data


@pytest.mark.asyncio
async def test_get_training_records(auth_headers: dict, async_client: AsyncClient):
    """GET /training/records returns user's training records."""
    # First create a training record
    mock_result = {"overall_score": 90, "dimensions": {}, "feedback": "Great!"}

    with patch(
        "app.api.v1.endpoints.training.evaluate_training",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        await async_client.post(
            "/api/v1/training/evaluate",
            json={
                "training_type": "belief",
                "input_data": {"text": "Belief transformation exercise"},
            },
            headers=auth_headers,
        )

    # Now fetch records
    response = await async_client.get("/api/v1/training/records", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
