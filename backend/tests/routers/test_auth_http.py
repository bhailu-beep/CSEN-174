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


def _register(client: TestClient, username: str, password: str):
    return client.post("/auth/register", json={"username": username, "password": password})


def test_register_accepts_a_valid_username_and_password(client: TestClient, users: AsyncMock) -> None:
    response = _register(client, "Ada_99", "secret1")

    assert response.status_code == 200
    assert response.json() == {"access_token": "access-token"}
    users.create_user.assert_awaited_once_with("Ada_99", "secret1")


@pytest.mark.parametrize(
    "username",
    ["ab", "a" * 21, "has space", "dash-ed", "dot.ted", "emoji\U0001f600", "", "bad\n"],
)
def test_register_rejects_an_invalid_username(client: TestClient, users: AsyncMock, username: str) -> None:
    response = _register(client, username, "secret1")

    assert response.status_code == 422
    users.create_user.assert_not_awaited()


@pytest.mark.parametrize("username", ["abc", "a" * 20, "Under_score_1"])
def test_register_accepts_usernames_at_the_length_limits(client: TestClient, username: str) -> None:
    assert _register(client, username, "secret1").status_code == 200


@pytest.mark.parametrize("password", ["", "12345"])
def test_register_rejects_a_short_password(client: TestClient, users: AsyncMock, password: str) -> None:
    response = _register(client, "ada", password)

    assert response.status_code == 422
    users.create_user.assert_not_awaited()


def test_register_accepts_a_password_of_exactly_72_bytes(client: TestClient) -> None:
    assert _register(client, "ada", "a" * 72).status_code == 200


def test_register_rejects_a_password_over_72_bytes(client: TestClient, users: AsyncMock) -> None:
    response = _register(client, "ada", "a" * 73)

    assert response.status_code == 422
    users.create_user.assert_not_awaited()


def test_register_counts_password_length_in_bytes_not_characters(client: TestClient, users: AsyncMock) -> None:
    # 40 two-byte characters is 40 characters but 80 bytes, which bcrypt cannot hash.
    response = _register(client, "ada", "é" * 40)

    assert response.status_code == 422
    users.create_user.assert_not_awaited()


@pytest.mark.parametrize("body", [{}, {"username": "ada"}, {"password": "secret1"}, {"username": 5, "password": 6}])
def test_register_rejects_a_missing_or_mistyped_field(client: TestClient, users: AsyncMock, body: dict) -> None:
    assert client.post("/auth/register", json=body).status_code == 422
    users.create_user.assert_not_awaited()


def test_register_reports_a_taken_username_as_400_not_422(client: TestClient, users: AsyncMock) -> None:
    users.create_user.return_value = None

    response = _register(client, "ada", "secret1")

    assert response.status_code == 400
    assert "already taken" in response.json()["detail"]


def test_login_still_accepts_credentials_that_register_would_reject(client: TestClient, users: AsyncMock) -> None:
    # Login only checks the password; old or odd accounts must still be able to sign in.
    response = client.post("/auth/login", json={"username": "x", "password": "short"})

    assert response.status_code == 200
    users.login.assert_awaited_once_with("x", "short")
