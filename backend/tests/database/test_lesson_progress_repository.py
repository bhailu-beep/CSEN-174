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
            yield LessonProgressRepository(conn)
    finally:
        DbConnection.pool = None


async def test_get_code_is_scoped_to_user_lesson_and_exercise(
    lesson_progress: LessonProgressRepository,
    db_pool: asyncpg.Pool,
) -> None:
    ada = await _insert_user(db_pool, "ada")
    grace = await _insert_user(db_pool, "grace")
    await lesson_progress.create_lesson_progress(ada, "basics", "sum", "ada-sum")
    await lesson_progress.create_lesson_progress(ada, "basics", "is-even", "ada-even")
    await lesson_progress.create_lesson_progress(grace, "basics", "sum", "grace-sum")

    assert await lesson_progress.get_code(ada, "basics", "sum") == "ada-sum"
    assert await lesson_progress.get_code(ada, "basics", "is-even") == "ada-even"
    assert await lesson_progress.get_code(grace, "basics", "sum") == "grace-sum"
    assert await lesson_progress.get_code(ada, "conditionals", "sum") is None


async def test_update_code_replaces_only_the_matching_row(
    lesson_progress: LessonProgressRepository,
    db_pool: asyncpg.Pool,
) -> None:
    user_id = await _insert_user(db_pool, "ada")
    await lesson_progress.create_lesson_progress(user_id, "basics", "sum", "before")
    await lesson_progress.create_lesson_progress(user_id, "basics", "is-even", "other")

    await lesson_progress.update_code(user_id, "basics", "sum", "after")

    assert await lesson_progress.get_code(user_id, "basics", "sum") == "after"
    assert await lesson_progress.get_code(user_id, "basics", "is-even") == "other"


async def test_update_code_creates_one_row_when_the_exercise_has_no_progress(
    lesson_progress: LessonProgressRepository,
    db_pool: asyncpg.Pool,
) -> None:
    user_id = await _insert_user(db_pool, "ada")

    await lesson_progress.update_code(user_id, "basics", "sum", "first")
    await lesson_progress.update_code(user_id, "basics", "sum", "second")

    assert await lesson_progress.get_code(user_id, "basics", "sum") == "second"
    async with db_pool.acquire() as connection:
        count = await connection.fetchval(
            "SELECT COUNT(*) FROM lesson_progress WHERE user_id = $1 AND lesson_id = $2 AND exercise_id = $3",
            user_id,
            "basics",
            "sum",
        )
    assert count == 1


async def test_clear_all_progress_deletes_only_that_user(
    lesson_progress: LessonProgressRepository,
    db_pool: asyncpg.Pool,
) -> None:
    ada = await _insert_user(db_pool, "ada")
    grace = await _insert_user(db_pool, "grace")
    await lesson_progress.create_lesson_progress(ada, "basics", "sum", "ada")
    await lesson_progress.create_lesson_progress(ada, "loops", "power", "ada-again")
    await lesson_progress.create_lesson_progress(grace, "basics", "sum", "grace")

    await lesson_progress.clear_all_progress(ada)

    assert await lesson_progress.get_code(ada, "basics", "sum") is None
    assert await lesson_progress.get_code(ada, "loops", "power") is None
    assert await lesson_progress.get_code(grace, "basics", "sum") == "grace"


async def test_count_completed_by_lesson_ignores_unfinished_and_other_users(
    lesson_progress: LessonProgressRepository,
    db_pool: asyncpg.Pool,
) -> None:
    ada = await _insert_user(db_pool, "ada")
    grace = await _insert_user(db_pool, "grace")
    await lesson_progress.create_lesson_progress(ada, "basics", "sum", "done")
    await lesson_progress.create_lesson_progress(ada, "basics", "is-even", "started")
    await lesson_progress.create_lesson_progress(ada, "loops", "power", "done")
    await lesson_progress.create_lesson_progress(grace, "basics", "sum", "done")
    await lesson_progress.mark_completed(ada, "basics", "sum")
    await lesson_progress.mark_completed(ada, "loops", "power")
    await lesson_progress.mark_completed(grace, "basics", "sum")

    assert await lesson_progress.count_completed_by_lesson(ada) == {"basics": 1, "loops": 1}
