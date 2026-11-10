from unittest.mock import AsyncMock

import pytest

from database.types.lesson import Exercise, Lesson
from database.types.lesson_progress import ExerciseProgress
from services.lesson_progress import LessonProgressService

USER_ID, LESSON_ID, EXERCISE_ID = 4, "conditionals", "leap-year"


@pytest.fixture
def repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def lessons() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(repository: AsyncMock, lessons: AsyncMock) -> LessonProgressService:
    return LessonProgressService(repository, lessons)


async def test_create_lesson_progress_forwards_to_the_repository(
    service: LessonProgressService, repository: AsyncMock
) -> None:
    await service.create_lesson_progress(USER_ID, LESSON_ID, EXERCISE_ID, "int x;")

    repository.create_lesson_progress.assert_awaited_once_with(USER_ID, LESSON_ID, EXERCISE_ID, "int x;")


async def test_get_code_returns_the_saved_code(service: LessonProgressService, repository: AsyncMock) -> None:
    repository.get_code.return_value = "int x;"

    assert await service.get_code(USER_ID, LESSON_ID, EXERCISE_ID) == "int x;"
    repository.get_code.assert_awaited_once_with(USER_ID, LESSON_ID, EXERCISE_ID)


async def test_get_code_returns_none_when_nothing_is_saved(
    service: LessonProgressService, repository: AsyncMock
) -> None:
    repository.get_code.return_value = None

    assert await service.get_code(USER_ID, LESSON_ID, EXERCISE_ID) is None


async def test_update_code_forwards_to_the_repository(service: LessonProgressService, repository: AsyncMock) -> None:
    await service.update_code(USER_ID, LESSON_ID, EXERCISE_ID, "int y;")

    repository.update_code.assert_awaited_once_with(USER_ID, LESSON_ID, EXERCISE_ID, "int y;")


async def test_mark_completed_forwards_to_the_repository(
    service: LessonProgressService, repository: AsyncMock
) -> None:
    await service.mark_completed(USER_ID, LESSON_ID, EXERCISE_ID)

    repository.mark_completed.assert_awaited_once_with(USER_ID, LESSON_ID, EXERCISE_ID)


async def test_clear_all_progress_only_targets_the_given_user(
    service: LessonProgressService, repository: AsyncMock
) -> None:
    await service.clear_all_progress(USER_ID)

    repository.clear_all_progress.assert_awaited_once_with(USER_ID)


@pytest.mark.parametrize(
    "call",
    [
        lambda service: service.create_lesson_progress(USER_ID, "missing", "sum", "int x;"),
        lambda service: service.get_code(USER_ID, "missing", "sum"),
        lambda service: service.update_code(USER_ID, "missing", "sum", "int y;"),
        lambda service: service.mark_completed(USER_ID, "missing", "sum"),
    ],
)
async def test_unknown_exercise_is_rejected_before_progress_is_touched(
    repository: AsyncMock, lessons: AsyncMock, call
) -> None:
    lessons.get_exercise.side_effect = ValueError("Exercise sum not found in lesson missing")
    service = LessonProgressService(repository, lessons)

    with pytest.raises(ValueError, match="not found"):
        await call(service)

    repository.create_lesson_progress.assert_not_awaited()
    repository.get_code.assert_not_awaited()
    repository.update_code.assert_not_awaited()
    repository.mark_completed.assert_not_awaited()


def _catalog() -> dict[Lesson, list[Exercise]]:
    return {
        Lesson(id="basics", name="Basics"): [
            Exercise(id="sum", lesson_id="basics", tester_code="", tests=[]),
            Exercise(id="is-even", lesson_id="basics", tester_code="", tests=[]),
            Exercise(id="to-fahrenheit", lesson_id="basics", tester_code="", tests=[]),
        ],
        Lesson(id="loops", name="Loops"): [
            Exercise(id="power", lesson_id="loops", tester_code="", tests=[]),
        ],
    }


async def test_get_lesson_progress_lists_every_exercise_in_catalog_order(
    service: LessonProgressService, repository: AsyncMock, lessons: AsyncMock
) -> None:
    lessons.get_lessons.return_value = _catalog()
    repository.get_lesson_progress.return_value = [
        ExerciseProgress(exercise_id="is-even", completed=True, started=True),
    ]

    progress = await service.get_lesson_progress(USER_ID, "basics")

    assert progress == [
        ExerciseProgress(exercise_id="sum", completed=False, started=False),
        ExerciseProgress(exercise_id="is-even", completed=True, started=True),
        ExerciseProgress(exercise_id="to-fahrenheit", completed=False, started=False),
    ]
    repository.get_lesson_progress.assert_awaited_once_with(USER_ID, "basics")


async def test_get_lesson_progress_ignores_saved_rows_for_exercises_no_longer_in_the_catalog(
    service: LessonProgressService, repository: AsyncMock, lessons: AsyncMock
) -> None:
    lessons.get_lessons.return_value = _catalog()
    repository.get_lesson_progress.return_value = [
        ExerciseProgress(exercise_id="deleted-exercise", completed=True, started=True),
    ]

    progress = await service.get_lesson_progress(USER_ID, "loops")

    assert progress == [ExerciseProgress(exercise_id="power", completed=False, started=False)]


async def test_get_lesson_progress_rejects_an_unknown_lesson(
    service: LessonProgressService, repository: AsyncMock, lessons: AsyncMock
) -> None:
    lessons.get_lessons.return_value = _catalog()

    with pytest.raises(ValueError, match="Lesson missing not found"):
        await service.get_lesson_progress(USER_ID, "missing")

    repository.get_lesson_progress.assert_not_awaited()
