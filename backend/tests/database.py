from __future__ import annotations

import asyncio
from collections.abc import Iterator
from pathlib import Path

import asyncpg
import pytest
from docker.errors import DockerException
from testcontainers.community.postgres import PostgresContainer

POSTGRES_IMAGE = "postgres:16-alpine"
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "setup.sql"


def _apply_schema(container: PostgresContainer) -> None:
    result = container.exec(
        [
            "psql",
            "--username",
            container.username,
            "--dbname",
            container.dbname,
            "--set",
            "ON_ERROR_STOP=1",
            "--command",
            SCHEMA_PATH.read_text(encoding="utf-8"),
        ]
    )
    if result.exit_code != 0:
        raise RuntimeError(result.output.decode(errors="replace"))


def _start_postgres() -> PostgresContainer:
    container = PostgresContainer(
        POSTGRES_IMAGE,
        username="completec_test",
        password="completec_test",
        dbname="completec_test",
        driver=None,
    )
    try:
        container.start()
    except DockerException:
        container.stop()
        raise
    return container


@pytest.fixture(scope="session")
def ephemeral_postgres() -> Iterator[PostgresContainer]:
    """Start a throwaway Postgres container and drop it when the session ends."""
    try:
        container = _start_postgres()
    except DockerException as exc:
        pytest.skip(f"Docker is required for the ephemeral Postgres database: {exc}")

    try:
        _apply_schema(container)
        yield container
    finally:
        container.stop()


async def create_pool(container: PostgresContainer) -> asyncpg.Pool:
    last_error: Exception | None = None
    for _ in range(20):
        try:
            return await asyncpg.create_pool(
                host=container.get_container_host_ip(),
                port=container.get_exposed_port(5432),
                user=container.username,
                password=container.password,
                database=container.dbname,
                min_size=1,
                max_size=2,
                timeout=2,
            )
        except (OSError, asyncpg.PostgresError) as exc:
            last_error = exc
            await asyncio.sleep(0.3)
    assert last_error is not None
    raise last_error