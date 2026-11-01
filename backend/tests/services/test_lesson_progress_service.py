from unittest.mock import AsyncMock

import pytest

from services.lesson_progress import LessonProgressService

USER_ID, CHAPTER_ID, LESSON_ID = 4, 2, 7


@pytest.fixture
def repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(repository: AsyncMock) -> LessonProgressService:
    return LessonProgressService(repository)


async def test_create_lesson_progress_forwards_to_the_repository(
    service: LessonProgressService, repository: AsyncMock
) -> None:
    await service.create_lesson_progress(USER_ID, CHAPTER_ID, LESSON_ID, "int x;")

    repository.create_lesson_progress.assert_awaited_once_with(USER_ID, CHAPTER_ID, LESSON_ID, "int x;")


async def test_get_code_returns_the_saved_code(service: LessonProgressService, repository: AsyncMock) -> None:
    repository.get_code.return_value = "int x;"

    assert await service.get_code(USER_ID, CHAPTER_ID, LESSON_ID) == "int x;"
    repository.get_code.assert_awaited_once_with(USER_ID, CHAPTER_ID, LESSON_ID)


async def test_get_code_returns_none_when_nothing_is_saved(
    service: LessonProgressService, repository: AsyncMock
) -> None:
    repository.get_code.return_value = None

    assert await service.get_code(USER_ID, CHAPTER_ID, LESSON_ID) is None


async def test_update_code_forwards_to_the_repository(service: LessonProgressService, repository: AsyncMock) -> None:
    await service.update_code(USER_ID, CHAPTER_ID, LESSON_ID, "int y;")

    repository.update_code.assert_awaited_once_with(USER_ID, CHAPTER_ID, LESSON_ID, "int y;")


async def test_mark_completed_forwards_to_the_repository(
    service: LessonProgressService, repository: AsyncMock
) -> None:
    await service.mark_completed(USER_ID, CHAPTER_ID, LESSON_ID)

    repository.mark_completed.assert_awaited_once_with(USER_ID, CHAPTER_ID, LESSON_ID)


async def test_clear_all_progress_only_targets_the_given_user(
    service: LessonProgressService, repository: AsyncMock
) -> None:
    await service.clear_all_progress(USER_ID)

    repository.clear_all_progress.assert_awaited_once_with(USER_ID)


async def test_repository_errors_propagate(service: LessonProgressService, repository: AsyncMock) -> None:
    repository.mark_completed.side_effect = RuntimeError("db down")

    with pytest.raises(RuntimeError, match="db down"):
        await service.mark_completed(USER_ID, CHAPTER_ID, LESSON_ID)
