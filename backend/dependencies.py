from collections.abc import AsyncIterator

from asyncpg import Connection
from fastapi import Cookie, Depends, HTTPException
from database.connection import DbConnection
from database.types.lesson_progress import LessonProgressRepository
from database.types.user import User, UserRepository
from services.lesson_progress import LessonProgressService
from services.user import UserService


async def get_connection() -> AsyncIterator[Connection]:
    if DbConnection.pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with DbConnection.pool.acquire() as connection:
        yield connection


def get_user_repository(connection: Connection = Depends(get_connection)) -> UserRepository:
    return UserRepository(connection)


def get_lesson_progress_repository(
    connection: Connection = Depends(get_connection),
) -> LessonProgressRepository:
    return LessonProgressRepository(connection)


def get_user_service(repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repository)


def get_lesson_progress_service(
    repository: LessonProgressRepository = Depends(get_lesson_progress_repository),
) -> LessonProgressService:
    return LessonProgressService(repository)


async def get_current_user(
    users: UserService = Depends(get_user_service),
    access_token: str | None = Cookie(default=None),
) -> User:
    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await users.user_from_token(access_token)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
