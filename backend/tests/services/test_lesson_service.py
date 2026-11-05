from unittest.mock import AsyncMock

from database.types.lesson import Exercise, Lesson, LessonOverview
from services.lesson import LessonService


def _exercise(lesson_id: str, exercise_id: str) -> Exercise:
    return Exercise(id=exercise_id, lesson_id=lesson_id, tester_code="", tests=[])


async def test_get_lessons_keeps_each_lessons_completed_count() -> None:
    basics = Lesson(id="basics", name="Basics")
    loops = Lesson(id="loops", name="Loops")
    catalog = AsyncMock()
    catalog.get_lessons.return_value = {
        basics: [_exercise("basics", "sum"), _exercise("basics", "is-even")],
        loops: [_exercise("loops", "power")],
    }
    progress = AsyncMock()
    progress.count_completed_by_lesson.return_value = {"basics": 1}
    service = LessonService(catalog, progress)

    lessons = await service.get_lessons(4)

    assert lessons == [
        LessonOverview(id="basics", name="Basics", exercise_count=2, completed_count=1),
        LessonOverview(id="loops", name="Loops", exercise_count=1, completed_count=0),
    ]
    progress.count_completed_by_lesson.assert_awaited_once_with(4)
