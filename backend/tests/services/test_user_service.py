from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock

import bcrypt
import jwt
import pytest
from database.types.user import User
from services.user import _DUMMY_PASSWORD_HASH, UserService

JWT_SECRET = "test-secret-with-enough-bytes-for-hs256"


@pytest.fixture(autouse=True)
def jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", JWT_SECRET)


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


def _token(**claims: object) -> str:
    return jwt.encode(claims, JWT_SECRET, algorithm="HS256")


# --- authenticate_user ---


async def test_correct_password_authenticates_user() -> None:
    user = _user("secret")

    assert await _service(user).authenticate_user("ada", "secret") == user


async def test_incorrect_password_returns_none() -> None:
    assert await _service(_user("secret")).authenticate_user("ada", "wrong") is None


async def test_authenticate_user_looks_up_the_given_username() -> None:
    service = _service(_user("secret"))

    await service.authenticate_user("ada", "secret")

    service.user_repository.get_user_by_username.assert_awaited_once_with("ada")


async def test_unknown_user_still_runs_a_dummy_password_check(monkeypatch: pytest.MonkeyPatch) -> None:
    service = _service(None)
    password_matches = Mock(return_value=False)
    monkeypatch.setattr(service, "_password_matches", password_matches)

    assert await service.authenticate_user("ghost", "secret") is None
    password_matches.assert_called_once_with("secret", _DUMMY_PASSWORD_HASH)


# --- login ---


async def test_login_issues_a_token_for_the_user() -> None:
    token = await _service(_user("secret")).login("ada", "secret")

    assert token is not None
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    assert payload["sub"] == "4"
    assert payload["username"] == "ada"


async def test_login_rejects_a_wrong_password() -> None:
    assert await _service(_user("secret")).login("ada", "wrong") is None


async def test_login_rejects_an_unknown_user() -> None:
    assert await _service(None).login("ada", "secret") is None


# --- create_user ---


async def test_create_user_stores_a_hash_and_returns_a_token() -> None:
    repository = AsyncMock()
    repository.create_user.side_effect = lambda username, hashed: User(
        id=9, username=username, hashed_password=hashed
    )

    token = await UserService(repository).create_user("grace", "secret")

    stored_username, stored_hash = repository.create_user.await_args.args
    assert stored_username == "grace"
    assert stored_hash != "secret"
    assert bcrypt.checkpw(b"secret", stored_hash.encode("utf-8"))
    assert token is not None
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    assert payload["sub"] == "9"
    assert payload["username"] == "grace"


# --- user_from_token ---


async def test_user_from_token_loads_the_user() -> None:
    user = _user("secret")
    service = _service(user)
    service.user_repository.get_user_by_id.return_value = user
    token = await service.login("ada", "secret")

    assert token is not None
    assert await service.user_from_token(token) == user
    service.user_repository.get_user_by_id.assert_awaited_once_with(4)


async def test_user_from_token_rejects_a_bad_token() -> None:
    assert await _service(_user("secret")).user_from_token("not-a-token") is None


async def test_user_from_token_rejects_a_token_signed_with_another_secret() -> None:
    forged = jwt.encode({"sub": "4"}, "some-other-secret-with-enough-bytes-xx", algorithm="HS256")

    assert await _service(_user("secret")).user_from_token(forged) is None


async def test_user_from_token_rejects_an_expired_token() -> None:
    service = _service(_user("secret"))
    expired = _token(sub="4", exp=datetime.now(timezone.utc) - timedelta(minutes=1))

    assert await service.user_from_token(expired) is None
    service.user_repository.get_user_by_id.assert_not_awaited()


async def test_user_from_token_rejects_a_non_numeric_subject() -> None:
    service = _service(_user("secret"))

    assert await service.user_from_token(_token(sub="abc")) is None
    service.user_repository.get_user_by_id.assert_not_awaited()


async def test_user_from_token_rejects_a_missing_subject() -> None:
    assert await _service(_user("secret")).user_from_token(_token(username="ada")) is None


async def test_user_from_token_returns_none_when_user_no_longer_exists() -> None:
    service = _service(_user("secret"))
    service.user_repository.get_user_by_id.side_effect = ValueError("missing")
    token = await service.login("ada", "secret")

    assert token is not None
    assert await service.user_from_token(token) is None
