from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services.ab_testing import get_experiment

router = APIRouter(prefix="/ab", tags=["ab_testing"])


@router.get("/experiment/{experiment_name}")
async def get_ab_variant(
    experiment_name: str,
    user_id: str = Query(..., description="User ID for deterministic assignment"),
):
    """
    Returns the A/B testing variant assigned to the user for a given experiment.
    Deterministic: same user + experiment always returns the same variant.
    """
    variant = get_experiment(user_id, experiment_name)
    if variant is None:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment '{experiment_name}' not found",
        )
    return {
        "experiment": experiment_name,
        "user_id": user_id,
        "variant": variant,
    }
