from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials
from starlette.datastructures import Headers

from database.types.user import User
from dependencies import get_current_user
from routers.auth import (
    AccessTokenResponse,
    LoginRequest,
    PublicUser,
    RegisterRequest,
    login,
    logout,
    me,
    refresh,
    register,
)
from services.user import TokenPair

USER = User(id=4, username="ada", hashed_password="irrelevant")
TOKENS = TokenPair(access_token="access-token", refresh_token="refresh-token")


def _users(tokens: TokenPair | None = TOKENS, user: User | None = USER) -> AsyncMock:
    users = AsyncMock()
    users.login.return_value = tokens
    users.create_user.return_value = tokens
    users.refresh.return_value = tokens
    users.user_from_token.return_value = user
    return users


def _request_with_cookie(cookie: str | None = None) -> Request:
    headers = Headers({"cookie": f"refresh_token={cookie}"} if cookie else {})
    return Request({"type": "http", "headers": headers.raw, "method": "POST", "path": "/auth/refresh"})


async def test_login_route_sets_a_refresh_cookie() -> None:
    response = Response()

    body = await login(LoginRequest(username="ada", password="secret"), response, user_service=_users())

    assert body == AccessTokenResponse(access_token="access-token")
    cookie = response.headers["set-cookie"].lower()
    assert "refresh_token=refresh-token" in cookie
    assert "httponly" in cookie
    assert "path=/auth" in cookie
    assert "access_token=" not in cookie


async def test_login_route_rejects_invalid_credentials() -> None:
    with pytest.raises(HTTPException) as exc:
        await login(LoginRequest(username="ada", password="wrong"), Response(), user_service=_users(tokens=None))

    assert exc.value.status_code == 401


async def test_refresh_route_issues_a_new_access_token() -> None:
    response = Response()
    users = _users()

    body = await refresh(_request_with_cookie("old-refresh"), response, user_service=users)

    assert body == AccessTokenResponse(access_token="access-token")
    users.refresh.assert_awaited_once_with("old-refresh")
    cookie = response.headers["set-cookie"].lower()
    assert "refresh_token=refresh-token" in cookie
    assert "httponly" in cookie


async def test_refresh_route_rejects_a_missing_cookie() -> None:
    with pytest.raises(HTTPException) as exc:
        await refresh(_request_with_cookie(), Response(), user_service=_users())

    assert exc.value.status_code == 401


async def test_refresh_route_rejects_an_invalid_refresh_token() -> None:
    with pytest.raises(HTTPException) as exc:
        await refresh(
            _request_with_cookie("bad-refresh"),
            Response(),
            user_service=_users(tokens=None),
        )

    assert exc.value.status_code == 401


async def test_get_current_user_returns_the_user_for_a_valid_token() -> None:
    credential = HTTPAuthorizationCredentials(scheme="Bearer", credentials="signed-token")

    assert await get_current_user(users=_users(), credential=credential) == USER


async def test_get_current_user_rejects_an_invalid_token() -> None:
    credential = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad")

    with pytest.raises(HTTPException) as exc:
        await get_current_user(users=_users(user=None), credential=credential)

    assert exc.value.status_code == 401


async def test_me_returns_the_user_without_the_password_hash() -> None:
    assert await me(USER) == PublicUser(id=4, username="ada")


async def test_register_route_sets_a_refresh_cookie() -> None:
    response = Response()
    users = _users()

    body = await register(RegisterRequest(username="grace", password="secret"), response, user_service=users)

    assert body == AccessTokenResponse(access_token="access-token")
    users.create_user.assert_awaited_once_with("grace", "secret")
    cookie = response.headers["set-cookie"].lower()
    assert "refresh_token=refresh-token" in cookie
    assert "httponly" in cookie
    assert "access_token=" not in cookie


async def test_register_route_returns_400_when_registration_fails() -> None:
    users = _users(tokens=None)

    with pytest.raises(HTTPException) as exc:
        await register(RegisterRequest(username="grace", password="secret"), Response(), user_service=users)

    assert exc.value.status_code == 400


async def test_register_route_explains_that_the_username_is_taken() -> None:
    users = _users()
    users.create_user.return_value = None

    with pytest.raises(HTTPException) as exc:
        await register(RegisterRequest(username="grace", password="secret"), Response(), user_service=users)

    assert "already taken" in exc.value.detail


async def test_logout_route_clears_the_refresh_cookie() -> None:
    response = Response()

    assert await logout(response) is None

    cookie = response.headers["set-cookie"].lower()
    assert "refresh_token=" in cookie
    assert "max-age=0" in cookie
    assert "path=/auth" in cookie
    assert "httponly" in cookie


async def test_logout_route_does_not_touch_the_user_service() -> None:
    users = _users()

    await logout(Response())

    users.user_from_token.assert_not_awaited()
    users.refresh.assert_not_awaited()
