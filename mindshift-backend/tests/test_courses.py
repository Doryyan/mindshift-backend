from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_courses(auth_headers: dict, async_client: AsyncClient):
    """GET /courses returns a list of courses."""
    response = await async_client.get("/api/v1/courses", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_courses_filter_by_level(auth_headers: dict, async_client: AsyncClient):
    """GET /courses?level=beginner filters by level correctly."""
    response = await async_client.get(
        "/api/v1/courses", headers=auth_headers, params={"level": "beginner"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for course in data:
        assert course.get("level") == "beginner"


@pytest.mark.asyncio
async def test_get_course_detail(auth_headers: dict, async_client: AsyncClient):
    """GET /courses/{id} returns course with lessons."""
    # First list all courses to find a valid ID
    list_response = await async_client.get("/api/v1/courses", headers=auth_headers)
    courses = list_response.json()

    if not courses:
        pytest.skip("No courses in database to test")

    course_id = courses[0]["id"]
    response = await async_client.get(f"/api/v1/courses/{course_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == course_id
    assert "title" in data
    assert "lessons" in data


@pytest.mark.asyncio
async def test_get_course_not_found(auth_headers: dict, async_client: AsyncClient):
    """GET /courses/{id} with nonexistent ID returns 404."""
    response = await async_client.get("/api/v1/courses/nonexistent-id", headers=auth_headers)
    assert response.status_code == 404
