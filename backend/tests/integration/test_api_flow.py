"""The flow the frontend performs, through the real routers, services and database."""

import uuid

import httpx
import pytest

pytestmark = pytest.mark.docker

CORRECT = "int sum(int a, int b) { return a + b; }"
WRONG = "int sum(int a, int b) { return 0; }"
EXERCISE = "/lessons/basics/exercises/sum"


def _username() -> str:
    return "u" + uuid.uuid4().hex[:12]


async def _register(client: httpx.AsyncClient, username: str | None = None) -> dict[str, str]:
    response = await client.post("/auth/register", json={"username": username or _username(), "password": "secret1"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def test_register_sets_a_refresh_cookie_that_restores_the_session(client: httpx.AsyncClient) -> None:
    username = _username()
    headers = await _register(client, username)

    assert (await client.get("/auth/me", headers=headers)).json()["username"] == username

    # The cookie jar plays the browser: refresh with no Authorization header, then use the new token.
    refreshed = await client.post("/auth/refresh")
    assert refreshed.status_code == 200
    new_headers = {"Authorization": f"Bearer {refreshed.json()['access_token']}"}
    assert (await client.get("/auth/me", headers=new_headers)).status_code == 200


async def test_logout_clears_the_cookie_so_refresh_fails(client: httpx.AsyncClient) -> None:
    await _register(client)

    assert (await client.post("/auth/logout")).status_code == 204
    assert (await client.post("/auth/refresh")).status_code == 401


async def test_usernames_are_unique_ignoring_case(client: httpx.AsyncClient) -> None:
    username = _username()
    await _register(client, username)

    again = await client.post("/auth/register", json={"username": username.upper(), "password": "secret1"})

    assert again.status_code == 400


async def test_wrong_password_is_rejected(client: httpx.AsyncClient) -> None:
    username = _username()
    await _register(client, username)

    response = await client.post("/auth/login", json={"username": username, "password": "nope-nope"})

    assert response.status_code == 401


async def test_protected_routes_need_a_token_but_tests_are_public(client: httpx.AsyncClient) -> None:
    assert (await client.get("/lessons/basics/progress")).status_code in (401, 403)
    public = await client.get(f"{EXERCISE}/tests")
    assert public.status_code == 200
    assert public.json()[0]["expected"] == "5"


async def test_saved_code_and_started_status_round_trip(client: httpx.AsyncClient) -> None:
    headers = await _register(client)

    assert (await client.get(f"{EXERCISE}/code", headers=headers)).json() == ""
    await client.put(f"{EXERCISE}/code", headers=headers, json={"code": WRONG})

    assert (await client.get(f"{EXERCISE}/code", headers=headers)).json() == WRONG
    progress = {p["exercise_id"]: p for p in (await client.get("/lessons/basics/progress", headers=headers)).json()}
    assert progress["sum"] == {"exercise_id": "sum", "completed": False, "started": True}
    assert progress["is-even"]["started"] is False


async def test_a_failing_then_passing_run_completes_the_exercise(client: httpx.AsyncClient) -> None:
    headers = await _register(client)

    failed = await client.post(f"{EXERCISE}/run", headers=headers, json={"code": WRONG})
    assert failed.json()["status"] == "failed"
    assert all(not t["passed"] for t in failed.json()["tests"])
    assert {p["exercise_id"]: p["completed"] for p in (await client.get("/lessons/basics/progress", headers=headers)).json()}["sum"] is False

    passed = await client.post(f"{EXERCISE}/run", headers=headers, json={"code": CORRECT})
    assert passed.json()["status"] == "passed"

    overview = {lesson["id"]: lesson for lesson in (await client.get("/lessons/", headers=headers)).json()}
    assert overview["basics"]["completed_count"] == 1


async def test_progress_is_per_user_and_reset_only_clears_the_callers(client: httpx.AsyncClient) -> None:
    ada = await _register(client)
    await client.post(f"{EXERCISE}/run", headers=ada, json={"code": CORRECT})
    client.cookies.clear()
    bob = await _register(client)
    await client.post(f"{EXERCISE}/run", headers=bob, json={"code": CORRECT})

    assert (await client.delete("/lessons/progress", headers=ada)).status_code == 204

    async def completed(headers: dict[str, str]) -> int:
        lessons = (await client.get("/lessons/", headers=headers)).json()
        return sum(lesson["completed_count"] for lesson in lessons)

    assert await completed(ada) == 0
    assert await completed(bob) == 1


async def test_unknown_lesson_and_exercise_are_404(client: httpx.AsyncClient) -> None:
    headers = await _register(client)

    assert (await client.get("/lessons/nope/progress", headers=headers)).status_code == 404
    assert (await client.put("/lessons/basics/exercises/nope/code", headers=headers, json={"code": "x"})).status_code == 404
    assert (await client.post("/lessons/basics/exercises/nope/run", headers=headers, json={"code": "x"})).status_code == 404
