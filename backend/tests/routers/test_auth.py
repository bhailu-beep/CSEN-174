from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials

from database.types.user import User
from dependencies import get_current_user
from routers.auth import LoginRequest, PublicUser, login, me

USER = User(id=4, username="ada", hashed_password="irrelevant")


def _users(token: str | None = "signed-token", user: User | None = USER) -> AsyncMock:
    users = AsyncMock()
    users.login.return_value = token
    users.user_from_token.return_value = user
    return users


async def test_login_route_sets_a_browser_cookie() -> None:
    response = Response()

    body = await login(LoginRequest(username="ada", password="secret"), response, user_service=_users())

    assert body == {"access_token": "signed-token"}
    cookie = response.headers["set-cookie"].lower()
    assert "access_token=signed-token" in cookie
    assert "httponly" in cookie


async def test_login_route_rejects_invalid_credentials() -> None:
    with pytest.raises(HTTPException) as exc:
        await login(LoginRequest(username="ada", password="wrong"), Response(), user_service=_users(token=None))

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
