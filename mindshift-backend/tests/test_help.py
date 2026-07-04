from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_categories(auth_headers: dict, async_client: AsyncClient):
    """GET /help/categories returns categories list."""
    response = await async_client.get("/api/v1/help/categories", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_search_articles(auth_headers: dict, async_client: AsyncClient):
    """GET /help/articles?keyword= searches and finds articles by keyword."""
    response = await async_client.get(
        "/api/v1/help/articles", headers=auth_headers, params={"keyword": "NLP"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_article(auth_headers: dict, async_client: AsyncClient):
    """GET /help/articles/{id} returns article detail."""
    # First list articles to get a valid ID
    list_response = await async_client.get("/api/v1/help/articles", headers=auth_headers)
    articles = list_response.json()

    if not articles:
        pytest.skip("No help articles in database to test")

    article_id = articles[0]["id"]
    response = await async_client.get(
        f"/api/v1/help/articles/{article_id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_id
    assert "title" in data
    assert "content" in data
