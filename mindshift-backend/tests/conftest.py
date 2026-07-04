from __future__ import annotations

from typing import AsyncGenerator
from uuid import uuid4

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base, get_db

# Import all models so Base.metadata knows about them
from app.models.user import User  # noqa: F401

# Override settings for testing
settings.DATABASE_URL = "sqlite+aiosqlite://"

# Create test engine and session factory
test_engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
test_async_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def create_test_db():
    """Create all tables before each test and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP client configured with ASGI transport."""
    from main import app

    # Override the get_db dependency to use test sessions
    async def override_get_db():
        async with test_async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def auth_headers(async_client: AsyncClient) -> dict:
    """Create a test user and return just the Authorization header dict."""
    email = f"test-{uuid4().hex[:8]}@test.com"
    password = "Test123456"
    nickname = "TestUser"

    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "nickname": nickname},
    )
    assert response.status_code == 201
    token_data = response.json()
    token = token_data["access_token"]

    return {"Authorization": f"Bearer {token}"}
