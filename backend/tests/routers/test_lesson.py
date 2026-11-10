from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from database.types.user import User
from database.types.lesson import LessonOverview
from models.result import SubmissionResult
from models.tests import TestCase
from routers.lesson import RunCodeRequest, get_code, get_lessons, get_tests, run_code, update_code

USER = User(id=4, username="ada", hashed_password="irrelevant")


async def test_code_routes_return_404_when_the_exercise_is_missing() -> None:
    progress = AsyncMock()
    progress.get_code.side_effect = ValueError("Exercise missing not found in lesson basics")
    progress.update_code.side_effect = ValueError("Exercise missing not found in lesson basics")

    with pytest.raises(HTTPException) as get_exc:
        await get_code(USER, "basics", "missing", progress)
    with pytest.raises(HTTPException) as update_exc:
        await update_code(USER, "basics", "missing", "int x;", progress)

    assert get_exc.value.status_code == 404
    assert update_exc.value.status_code == 404


async def test_run_route_returns_404_when_the_exercise_is_missing() -> None:
    lessons = AsyncMock()
    lessons.run_code.side_effect = ValueError("Exercise missing not found in lesson basics")

    with pytest.raises(HTTPException) as exc:
        await run_code("basics", "missing", RunCodeRequest(code="int x;"), USER, lessons)

    assert exc.value.status_code == 404


async def test_get_lessons_returns_the_overview_for_the_current_user() -> None:
    overview = [LessonOverview(id="basics", name="Basics", exercise_count=3, completed_count=1)]
    lessons = AsyncMock()
    lessons.get_lessons.return_value = overview

    assert await get_lessons(USER, lessons) == overview
    lessons.get_lessons.assert_awaited_once_with(USER.id)


async def test_get_code_returns_the_saved_code() -> None:
    progress = AsyncMock()
    progress.get_code.return_value = "int sum(int a, int b) { return a + b; }"

    assert await get_code(USER, "basics", "sum", progress) == "int sum(int a, int b) { return a + b; }"
    progress.get_code.assert_awaited_once_with(USER.id, "basics", "sum")


async def test_get_code_returns_an_empty_string_when_nothing_is_saved() -> None:
    progress = AsyncMock()
    progress.get_code.return_value = None

    assert await get_code(USER, "basics", "sum", progress) == ""


async def test_update_code_saves_the_code_for_the_current_user() -> None:
    progress = AsyncMock()

    assert await update_code(USER, "basics", "sum", "int x;", progress) is None
    progress.update_code.assert_awaited_once_with(USER.id, "basics", "sum", "int x;")


async def test_run_route_returns_the_submission_and_scopes_it_to_the_user() -> None:
    submission = SubmissionResult(status="passed", tests=[], message="")
    lessons = AsyncMock()
    lessons.run_code.return_value = submission

    result = await run_code("basics", "sum", RunCodeRequest(code="int x;"), USER, lessons)

    assert result is submission
    lessons.run_code.assert_awaited_once_with(USER.id, "basics", "sum", "int x;")


async def test_get_tests_returns_the_cases() -> None:
    cases = [TestCase(inputs=("2", "3"), expected="5")]
    lessons = AsyncMock()
    lessons.get_tests.return_value = cases

    assert await get_tests("basics", "sum", lessons) == cases


async def test_get_tests_returns_404_when_the_exercise_is_missing() -> None:
    lessons = AsyncMock()
    lessons.get_tests.return_value = None

    with pytest.raises(HTTPException) as exc:
        await get_tests("basics", "missing", lessons)

    assert exc.value.status_code == 404
