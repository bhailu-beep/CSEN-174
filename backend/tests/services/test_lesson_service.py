from unittest.mock import AsyncMock, MagicMock

from database.types.lesson import Exercise, Lesson, LessonOverview
from models.result import RunResult, Stage
from models.tests import TestCase, TestResult
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
    service = LessonService(catalog, progress, AsyncMock())

    lessons = await service.get_lessons(4)

    assert lessons == [
        LessonOverview(id="basics", name="Basics", exercise_count=2, completed_count=1),
        LessonOverview(id="loops", name="Loops", exercise_count=1, completed_count=0),
    ]
    progress.count_completed_by_lesson.assert_awaited_once_with(4)


def _finished(*tests: TestResult, timed_out: bool = False, stage: Stage = Stage.RUN) -> RunResult:
    return RunResult(
        ok=not timed_out and stage == Stage.RUN,
        stage=stage,
        stdout="",
        stderr="g++ error" if stage == Stage.COMPILE else "",
        exit_code=0,
        timed_out=timed_out,
        message="",
        tests=tests,
    )


async def test_run_code_marks_the_exercise_completed_when_every_test_passes() -> None:
    exercise = Exercise(
        id="sum",
        lesson_id="basics",
        tester_code="tester",
        tests=[TestCase(inputs=("2", "3"), expected="5")],
    )
    catalog = AsyncMock()
    catalog.get_exercise.return_value = exercise
    progress = AsyncMock()
    runner = MagicMock()
    runner.run.return_value = _finished(TestResult(passed=True, expected="5", actual="5"))
    service = LessonService(catalog, progress, runner)

    submission = await service.run_code(4, "basics", "sum", "return a + b;")

    assert submission.status == "passed"
    assert submission.tests[0].actual == "5"
    progress.mark_completed.assert_awaited_once_with(4, "basics", "sum")
    runner.run.assert_called_once_with("return a + b;", tester="tester", tests=exercise.tests)


async def test_run_code_does_not_mark_completed_when_a_test_fails() -> None:
    catalog = AsyncMock()
    catalog.get_exercise.return_value = _exercise("basics", "sum")
    progress = AsyncMock()
    runner = MagicMock()
    runner.run.return_value = _finished(TestResult(passed=False, expected="5", actual="0"))
    service = LessonService(catalog, progress, runner)

    submission = await service.run_code(4, "basics", "sum", "return 0;")

    assert submission.status == "failed"
    progress.mark_completed.assert_not_awaited()
