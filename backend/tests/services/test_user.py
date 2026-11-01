from unittest.mock import AsyncMock

import bcrypt
import jwt
import pytest
from database.types.user import User
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


async def test_correct_password_authenticates_user() -> None:
    user = _user("secret")

    assert await _service(user).authenticate_user("ada", "secret") == user


async def test_incorrect_password_returns_none() -> None:
    assert await _service(_user("secret")).authenticate_user("ada", "wrong") is None


async def test_authenticate_user_looks_up_the_given_username() -> None:
    service = _service(_user("secret"))

    await service.authenticate_user("ada", "secret")

    service.user_repository.get_user_by_username.assert_awaited_once_with("ada")


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


async def test_user_from_token_returns_none_when_user_no_longer_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-secret-with-enough-bytes-for-hs256")
    service = _service(_user("secret"))
    service.user_repository.get_user_by_id.side_effect = ValueError("missing")
    token = await service.login("ada", "secret")

    assert token is not None
    assert await service.user_from_token(token) is None
