"""HTTP-level tests for the lesson router: routing, auth, request bodies and JSON responses.

Only the lesson router is mounted, with services replaced by mocks, so no database or Docker is needed.
"""

from collections.abc import Iterator
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from database.types.lesson import LessonOverview
from database.types.lesson_progress import ExerciseProgress
from database.types.user import User
from dependencies import get_lesson_progress_service, get_lesson_service, get_user_service
from models.result import ScoredTest, SubmissionResult
from routers.lesson import router

USER = User(id=4, username="ada", hashed_password="irrelevant")
AUTH = {"Authorization": "Bearer good-token"}


@pytest.fixture
def users() -> AsyncMock:
    mock = AsyncMock()
    mock.user_from_token.side_effect = lambda token: USER if token == "good-token" else None
    return mock


@pytest.fixture
def lessons() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def progress() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def client(users: AsyncMock, lessons: AsyncMock, progress: AsyncMock) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_user_service] = lambda: users
    app.dependency_overrides[get_lesson_service] = lambda: lessons
    app.dependency_overrides[get_lesson_progress_service] = lambda: progress
    with TestClient(app) as test_client:
        yield test_client


AUTHENTICATED_ROUTES = [
    ("GET", "/lessons/"),
    ("GET", "/lessons/basics/progress"),
    ("GET", "/lessons/basics/exercises/sum/code"),
    ("PUT", "/lessons/basics/exercises/sum/code?code=x"),
    ("POST", "/lessons/basics/exercises/sum/run"),
]


@pytest.mark.parametrize(("method", "path"), AUTHENTICATED_ROUTES)
def test_routes_reject_requests_without_a_token(client: TestClient, method: str, path: str) -> None:
    response = client.request(method, path, json={"code": "x"} if method == "POST" else None)

    assert response.status_code in (401, 403)


@pytest.mark.parametrize(("method", "path"), AUTHENTICATED_ROUTES)
def test_routes_reject_an_invalid_token(client: TestClient, method: str, path: str) -> None:
    response = client.request(
        method,
        path,
        headers={"Authorization": "Bearer bad-token"},
        json={"code": "x"} if method == "POST" else None,
    )

    assert response.status_code == 401


def test_rejected_requests_never_reach_the_services(
    client: TestClient, lessons: AsyncMock, progress: AsyncMock
) -> None:
    client.post("/lessons/basics/exercises/sum/run", json={"code": "x"})
    client.get("/lessons/basics/exercises/sum/code")

    lessons.run_code.assert_not_awaited()
    progress.get_code.assert_not_awaited()


def test_get_lessons_serializes_the_overview(client: TestClient, lessons: AsyncMock) -> None:
    lessons.get_lessons.return_value = [
        LessonOverview(id="basics", name="Basics", exercise_count=3, completed_count=1)
    ]

    response = client.get("/lessons/", headers=AUTH)

    assert response.status_code == 200
    assert response.json() == [{"id": "basics", "name": "Basics", "exercise_count": 3, "completed_count": 1}]
    lessons.get_lessons.assert_awaited_once_with(USER.id)


def test_get_code_returns_saved_code_as_json_and_empty_string_when_none(
    client: TestClient, progress: AsyncMock
) -> None:
    progress.get_code.return_value = "int x;"
    assert client.get("/lessons/basics/exercises/sum/code", headers=AUTH).json() == "int x;"

    progress.get_code.return_value = None
    assert client.get("/lessons/basics/exercises/sum/code", headers=AUTH).json() == ""


def test_get_code_for_an_unknown_exercise_is_404(client: TestClient, progress: AsyncMock) -> None:
    progress.get_code.side_effect = ValueError("Exercise nope not found in lesson basics")

    response = client.get("/lessons/basics/exercises/nope/code", headers=AUTH)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_put_code_saves_the_query_parameter_for_the_current_user(client: TestClient, progress: AsyncMock) -> None:
    response = client.put("/lessons/basics/exercises/sum/code", params={"code": "int y;"}, headers=AUTH)

    assert response.status_code == 200
    progress.update_code.assert_awaited_once_with(USER.id, "basics", "sum", "int y;")


def test_put_code_without_code_is_a_validation_error(client: TestClient, progress: AsyncMock) -> None:
    response = client.put("/lessons/basics/exercises/sum/code", headers=AUTH)

    assert response.status_code == 422
    progress.update_code.assert_not_awaited()


def test_run_returns_the_scored_submission_shape(client: TestClient, lessons: AsyncMock) -> None:
    lessons.run_code.return_value = SubmissionResult(
        status="failed",
        tests=[ScoredTest(passed=False, expected="5", actual="0")],
        message="",
    )

    response = client.post("/lessons/basics/exercises/sum/run", json={"code": "return 0;"}, headers=AUTH)

    assert response.status_code == 200
    assert response.json() == {
        "status": "failed",
        "tests": [{"passed": False, "expected": "5", "actual": "0"}],
        "message": "",
        "compiler_output": None,
    }
    lessons.run_code.assert_awaited_once_with(USER.id, "basics", "sum", "return 0;")


@pytest.mark.parametrize("body", [{}, {"code": 5}, {"source": "x"}])
def test_run_rejects_a_bad_body(client: TestClient, lessons: AsyncMock, body: dict) -> None:
    response = client.post("/lessons/basics/exercises/sum/run", json=body, headers=AUTH)

    assert response.status_code == 422
    lessons.run_code.assert_not_awaited()


def test_run_for_an_unknown_exercise_is_404(client: TestClient, lessons: AsyncMock) -> None:
    lessons.run_code.side_effect = ValueError("Exercise nope not found in lesson basics")

    response = client.post("/lessons/basics/exercises/nope/run", json={"code": "x"}, headers=AUTH)

    assert response.status_code == 404


def test_get_tests_unknown_exercise_is_404(client: TestClient, lessons: AsyncMock) -> None:
    lessons.get_tests.return_value = None

    assert client.get("/lessons/basics/exercises/nope/tests").status_code == 404


def test_get_lesson_progress_serializes_each_exercise(client: TestClient, progress: AsyncMock) -> None:
    progress.get_lesson_progress.return_value = [
        ExerciseProgress(exercise_id="sum", completed=True, started=True),
        ExerciseProgress(exercise_id="is-even", completed=False, started=False),
    ]

    response = client.get("/lessons/basics/progress", headers=AUTH)

    assert response.status_code == 200
    assert response.json() == [
        {"exercise_id": "sum", "completed": True, "started": True},
        {"exercise_id": "is-even", "completed": False, "started": False},
    ]
    progress.get_lesson_progress.assert_awaited_once_with(USER.id, "basics")


def test_get_lesson_progress_for_an_unknown_lesson_is_404(client: TestClient, progress: AsyncMock) -> None:
    progress.get_lesson_progress.side_effect = ValueError("Lesson missing not found")

    assert client.get("/lessons/missing/progress", headers=AUTH).status_code == 404
