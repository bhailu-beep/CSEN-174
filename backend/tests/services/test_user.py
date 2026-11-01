from unittest.mock import AsyncMock

import bcrypt
import jwt
import pytest
from fastapi import HTTPException, Response

from database.types.user import User
from dependencies import get_current_user
from routers.auth import LoginRequest, PublicUser, login, me
from services.user import UserService


def _user(password: str) -> User:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    return User(id=4, username="ada", hashed_password=hashed)


def _service(user: User | None) -> UserService:
    repository = AsyncMock()
    if user is None:
        repository.get_user_by_username.side_effect = ValueError("missing")
    else:
        repository.get_user_by_username.return_value = user
    return UserService(repository)


async def test_login_issues_a_token_for_the_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-secret-with-enough-bytes-for-hs256")
    token = await _service(_user("secret")).login("ada", "secret")

    assert token is not None
    payload = jwt.decode(token, "test-secret-with-enough-bytes-for-hs256", algorithms=["HS256"])
    assert payload["sub"] == "4"
    assert payload["username"] == "ada"


async def test_login_rejects_a_wrong_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-secret-with-enough-bytes-for-hs256")

    assert await _service(_user("secret")).login("ada", "wrong") is None


async def test_login_rejects_an_unknown_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-secret-with-enough-bytes-for-hs256")

    assert await _service(None).login("ada", "secret") is None


class _StubUsers:
    async def login(self, username: str, password: str) -> str | None:
        if password == "secret":
            return "signed-token"
        return None


async def test_login_route_sets_a_browser_cookie() -> None:
    response = Response()

    body = await login(LoginRequest(username="ada", password="secret"), response, users=_StubUsers())

    assert body == {"access_token": "signed-token"}
    cookie = response.headers["set-cookie"].lower()
    assert "access_token=signed-token" in cookie
    assert "httponly" in cookie


async def test_login_route_rejects_invalid_credentials() -> None:
    with pytest.raises(HTTPException) as exc:
        await login(LoginRequest(username="ada", password="wrong"), Response(), users=_StubUsers())

    assert exc.value.status_code == 401


async def test_user_from_token_loads_the_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-secret-with-enough-bytes-for-hs256")
    user = _user("secret")
    service = _service(user)
    service.user_repository.get_user_by_id.return_value = user
    token = await service.login("ada", "secret")

    assert token is not None
    assert await service.user_from_token(token) == user
    service.user_repository.get_user_by_id.assert_awaited_once_with(4)


async def test_user_from_token_rejects_a_bad_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-secret-with-enough-bytes-for-hs256")

    assert await _service(_user("secret")).user_from_token("not-a-token") is None


async def test_get_current_user_requires_a_cookie() -> None:
    with pytest.raises(HTTPException) as exc:
        await get_current_user(users=_service(_user("secret")), access_token=None)

    assert exc.value.status_code == 401


async def test_me_returns_the_user_without_the_password_hash() -> None:
    body = await me(_user("secret"))

    assert body == PublicUser(id=4, username="ada")
