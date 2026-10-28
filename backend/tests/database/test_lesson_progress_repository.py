from __future__ import annotations

from collections.abc import AsyncIterator

import asyncpg
import pytest
from database.connection import DbConnection
from database.types.lesson_progress import LessonProgressRepository


async def _insert_user(pool: asyncpg.Pool, username: str) -> int:
    async with pool.acquire() as conn:
        user_id = await conn.fetchval(
            "INSERT INTO users (username, hashed_password) VALUES ($1, $2) RETURNING id",
            username,
            "hash",
        )
    assert isinstance(user_id, int)
    return user_id


@pytest.fixture
async def lesson_progress(db_pool: asyncpg.Pool) -> AsyncIterator[LessonProgressRepository]:
    DbConnection.pool = db_pool
    try:
        async with db_pool.acquire() as conn:
            await conn.execute("TRUNCATE TABLE lesson_progress, users RESTART IDENTITY")
        yield LessonProgressRepository()
    finally:
        DbConnection.pool = None


async def test_get_code_is_scoped_to_user_chapter_and_lesson(
    lesson_progress: LessonProgressRepository,
    db_pool: asyncpg.Pool,
) -> None:
    ada = await _insert_user(db_pool, "ada")
    grace = await _insert_user(db_pool, "grace")
    await lesson_progress.create_lesson_progress(ada, 1, 1, "ada-1-1")
    await lesson_progress.create_lesson_progress(ada, 1, 2, "ada-1-2")
    await lesson_progress.create_lesson_progress(grace, 1, 1, "grace-1-1")

    assert await lesson_progress.get_code(ada, 1, 1) == "ada-1-1"
    assert await lesson_progress.get_code(ada, 1, 2) == "ada-1-2"
    assert await lesson_progress.get_code(grace, 1, 1) == "grace-1-1"
    assert await lesson_progress.get_code(ada, 2, 1) is None


async def test_update_code_replaces_only_the_matching_row(
    lesson_progress: LessonProgressRepository,
    db_pool: asyncpg.Pool,
) -> None:
    user_id = await _insert_user(db_pool, "ada")
    await lesson_progress.create_lesson_progress(user_id, 1, 1, "before")
    await lesson_progress.create_lesson_progress(user_id, 1, 2, "other")

    await lesson_progress.update_code(user_id, 1, 1, "after")

    assert await lesson_progress.get_code(user_id, 1, 1) == "after"
    assert await lesson_progress.get_code(user_id, 1, 2) == "other"


async def test_clear_all_progress_deletes_only_that_user(
    lesson_progress: LessonProgressRepository,
    db_pool: asyncpg.Pool,
) -> None:
    ada = await _insert_user(db_pool, "ada")
    grace = await _insert_user(db_pool, "grace")
    await lesson_progress.create_lesson_progress(ada, 1, 1, "ada")
    await lesson_progress.create_lesson_progress(ada, 2, 1, "ada-again")
    await lesson_progress.create_lesson_progress(grace, 1, 1, "grace")

    await lesson_progress.clear_all_progress(ada)

    assert await lesson_progress.get_code(ada, 1, 1) is None
    assert await lesson_progress.get_code(ada, 2, 1) is None
    assert await lesson_progress.get_code(grace, 1, 1) == "grace"
