"""HTTP-level tests for the auth router: cookies, status codes and routing through a real TestClient.

Only the auth router is mounted, with the user service replaced by a mock, so no database is needed.
"""

from collections.abc import Iterator
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from dependencies import get_user_service
from routers.auth import router
from services.user import TokenPair

TOKENS = TokenPair(access_token="access-token", refresh_token="refresh-token")


@pytest.fixture
def users() -> AsyncMock:
    mock = AsyncMock()
    mock.login.return_value = TOKENS
    mock.create_user.return_value = TOKENS
    mock.refresh.return_value = TOKENS
    return mock


@pytest.fixture
def client(users: AsyncMock) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_user_service] = lambda: users
    with TestClient(app) as test_client:
        yield test_client


def _log_in(client: TestClient) -> None:
    response = client.post("/auth/login", json={"username": "ada", "password": "secret"})
    assert response.status_code == 200


def test_logout_returns_204_with_no_body(client: TestClient) -> None:
    response = client.post("/auth/logout")

    assert response.status_code == 204
    assert response.content == b""


def test_logout_expires_the_refresh_cookie_on_the_auth_path(client: TestClient) -> None:
    response = client.post("/auth/logout")

    cookie = response.headers["set-cookie"].lower()
    assert "refresh_token=" in cookie
    assert "max-age=0" in cookie
    assert "path=/auth" in cookie


def test_logout_removes_the_cookie_that_login_set(client: TestClient, users: AsyncMock) -> None:
    _log_in(client)
    assert client.cookies.get("refresh_token") == "refresh-token"

    assert client.post("/auth/logout").status_code == 204

    assert client.cookies.get("refresh_token") is None


def test_refresh_is_rejected_after_logout(client: TestClient, users: AsyncMock) -> None:
    _log_in(client)
    client.post("/auth/logout")

    response = client.post("/auth/refresh")

    assert response.status_code == 401
    users.refresh.assert_not_awaited()


def test_logout_without_a_session_still_returns_204(client: TestClient) -> None:
    assert client.post("/auth/logout").status_code == 204
    assert client.post("/auth/logout").status_code == 204


def test_logout_does_not_require_an_access_token(client: TestClient, users: AsyncMock) -> None:
    response = client.post("/auth/logout", headers={"Authorization": "Bearer expired"})

    assert response.status_code == 204
    users.user_from_token.assert_not_awaited()
