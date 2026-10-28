from __future__ import annotations

from collections.abc import AsyncIterator

import asyncpg
import pytest
from database.connection import DbConnection
from database.types.user import User, UserRepository


@pytest.fixture
async def user_repository(db_pool: asyncpg.Pool) -> AsyncIterator[UserRepository]:
    DbConnection.pool = db_pool
    try:
        async with db_pool.acquire() as conn:
            await conn.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE")
        yield UserRepository()
    finally:
        DbConnection.pool = None


async def test_create_user_returns_the_inserted_row(user_repository: UserRepository) -> None:
    created = await user_repository.create_user("ada", "hash-1")

    assert created == User(id=1, username="ada", hashed_password="hash-1")


async def test_get_user_by_id_reads_the_stored_row(user_repository: UserRepository) -> None:
    created = await user_repository.create_user("ada", "hash-1")

    loaded = await user_repository.get_user_by_id(created.id)

    assert loaded == created


async def test_create_user_assigns_distinct_ids(user_repository: UserRepository) -> None:
    first = await user_repository.create_user("ada", "hash-1")
    second = await user_repository.create_user("grace", "hash-2")

    assert first.id == 1
    assert second.id == 2
    assert await user_repository.get_user_by_id(1) == first
    assert await user_repository.get_user_by_id(2) == second


async def test_values_are_stored_verbatim(user_repository: UserRepository) -> None:
    username = "o'hara"
    hashed_password = "p@ss'\"word"
    created = await user_repository.create_user(username, hashed_password)

    loaded = await user_repository.get_user_by_id(created.id)

    assert loaded.username == username
    assert loaded.hashed_password == hashed_password


async def test_get_user_by_id_unknown_id(user_repository: UserRepository) -> None:
    with pytest.raises(ValueError):
        await user_repository.get_user_by_id(999_999)
