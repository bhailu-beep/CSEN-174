"""Fixtures for integration tests: the real routers, services and repositories on a throwaway Postgres.

Only the C++ runner is faked, so these tests need Docker for the database but not the sandbox image.
"""

from collections.abc import AsyncIterator

import asyncpg
import httpx
import pytest
from fastapi import FastAPI

from dependencies import get_connection, get_cpp_runner
from models.result import RunResult, Stage
from models.tests import TestCase, TestResult
from routers import auth, lesson

# Reuse the ephemeral Postgres fixtures from the database tests.
from tests.database.conftest import db_pool, ephemeral_postgres  # noqa: F401

pytestmark = pytest.mark.docker


class FakeRunner:
    """Stands in for the Docker sandbox: code containing `return a + b` passes, anything else fails."""

    def run(self, code: str, *, tester: str, tests: list[TestCase]) -> RunResult:
        correct = "return a + b" in code
        results = tuple(
            TestResult(passed=correct, expected=case.expected, actual=case.expected if correct else "0")
            for case in tests
        )
        return RunResult(
            ok=True, stage=Stage.RUN, stdout="", stderr="", exit_code=0, timed_out=False, message="", tests=results
        )


@pytest.fixture
async def client(db_pool: asyncpg.Pool) -> AsyncIterator[httpx.AsyncClient]:  # noqa: F811
    app = FastAPI()
    app.include_router(auth.router)
    app.include_router(lesson.router)

    async def connection() -> AsyncIterator[asyncpg.Connection]:
        async with db_pool.acquire() as conn:
            yield conn

    app.dependency_overrides[get_connection] = connection
    app.dependency_overrides[get_cpp_runner] = lambda: FakeRunner()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http:
        yield http
