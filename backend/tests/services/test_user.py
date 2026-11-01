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
