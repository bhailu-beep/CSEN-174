from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from database.types.user import User
from routers.lesson import RunCodeRequest, get_code, run_code, update_code

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
