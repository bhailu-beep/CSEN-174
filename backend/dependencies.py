from collections.abc import AsyncIterator
from typing import Annotated

from asyncpg import Connection
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database.connection import DbConnection
from database.types.lesson import LessonRepository
from database.types.lesson_progress import LessonProgressRepository
from database.types.user import User, UserRepository
from services.lesson import LessonService
from services.lesson_progress import LessonProgressService
from services.user import UserService


async def get_connection() -> AsyncIterator[Connection]:
    if DbConnection.pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with DbConnection.pool.acquire() as connection:
        yield connection


def get_user_repository(connection: Annotated[Connection, Depends(get_connection)]) -> UserRepository:
    return UserRepository(connection)


def get_lesson_progress_repository(
    connection: Annotated[Connection, Depends(get_connection)],
) -> LessonProgressRepository:
    return LessonProgressRepository(connection)


# One catalog for the process. The repository reads the exercises folder on first use.
_lesson_repository = LessonRepository()


def get_lesson_repository() -> LessonRepository:
    return _lesson_repository


def get_lesson_service(
    repository: Annotated[LessonRepository, Depends(get_lesson_repository)],
) -> LessonService:
    return LessonService(repository)


def get_user_service(repository: Annotated[UserRepository, Depends(get_user_repository)]) -> UserService:
    return UserService(repository)


def get_lesson_progress_service(
    repository: Annotated[LessonProgressRepository, Depends(get_lesson_progress_repository)],
) -> LessonProgressService:
    return LessonProgressService(repository)


async def get_current_user(
    users: Annotated[UserService, Depends(get_user_service)],
    credential: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
) -> User:
    user = await users.user_from_token(credential.credentials)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        )
    return user
