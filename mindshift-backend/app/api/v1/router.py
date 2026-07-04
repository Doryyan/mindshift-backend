from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    courses,
    training,
    roleplay,
    cases,
    community,
    help,
    membership,
    progress,
    recommendations,
    challenge,
    ab_testing_endpoints,
    referral,
    growth,
    sync,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(courses.router)
api_router.include_router(training.router)
api_router.include_router(roleplay.router)
api_router.include_router(cases.router)
api_router.include_router(community.router)
api_router.include_router(help.router)
api_router.include_router(membership.router)
api_router.include_router(progress.router)
api_router.include_router(recommendations.router)
api_router.include_router(challenge.router)
api_router.include_router(ab_testing_endpoints.router)
api_router.include_router(referral.router)
api_router.include_router(growth.router)
api_router.include_router(sync.router)
