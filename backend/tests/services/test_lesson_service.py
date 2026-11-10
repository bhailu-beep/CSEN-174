from unittest.mock import AsyncMock, MagicMock

import pytest

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


@pytest.mark.parametrize(
    "result",
    [
        _finished(stage=Stage.COMPILE),
        _finished(timed_out=True),
        _finished(),
        RunResult.error("Docker is not available."),
    ],
    ids=["compilation_error", "timeout", "execution_error", "runner_error"],
)
async def test_run_code_does_not_mark_completed_for_non_passing_statuses(result: RunResult) -> None:
    catalog = AsyncMock()
    catalog.get_exercise.return_value = _exercise("basics", "sum")
    progress = AsyncMock()
    runner = MagicMock()
    runner.run.return_value = result
    service = LessonService(catalog, progress, runner)

    submission = await service.run_code(4, "basics", "sum", "code")

    assert submission.status != "passed"
    progress.mark_completed.assert_not_awaited()


async def test_run_code_does_not_mark_completed_when_only_some_tests_pass() -> None:
    catalog = AsyncMock()
    catalog.get_exercise.return_value = _exercise("basics", "sum")
    progress = AsyncMock()
    runner = MagicMock()
    runner.run.return_value = _finished(
        TestResult(passed=True, expected="5", actual="5"),
        TestResult(passed=False, expected="4", actual="0"),
    )
    service = LessonService(catalog, progress, runner)

    submission = await service.run_code(4, "basics", "sum", "code")

    assert submission.status == "failed"
    progress.mark_completed.assert_not_awaited()


async def test_run_code_for_an_unknown_exercise_never_reaches_the_runner() -> None:
    catalog = AsyncMock()
    catalog.get_exercise.side_effect = ValueError("Exercise nope not found in lesson basics")
    progress = AsyncMock()
    runner = MagicMock()
    service = LessonService(catalog, progress, runner)

    with pytest.raises(ValueError, match="not found"):
        await service.run_code(4, "basics", "nope", "code")

    runner.run.assert_not_called()
    progress.mark_completed.assert_not_awaited()


async def test_run_code_reports_compiler_output_for_a_compile_failure() -> None:
    catalog = AsyncMock()
    catalog.get_exercise.return_value = _exercise("basics", "sum")
    runner = MagicMock()
    runner.run.return_value = _finished(stage=Stage.COMPILE)
    service = LessonService(catalog, AsyncMock(), runner)

    submission = await service.run_code(4, "basics", "sum", "int sum(")

    assert submission.status == "compilation_error"
    assert submission.compiler_output == "g++ error"


async def test_get_tests_returns_the_exercises_cases() -> None:
    cases = [TestCase(inputs=("2", "3"), expected="5")]
    catalog = AsyncMock()
    catalog.get_exercise.return_value = Exercise(id="sum", lesson_id="basics", tester_code="", tests=cases)
    service = LessonService(catalog, AsyncMock(), MagicMock())

    assert await service.get_tests("basics", "sum") == cases


async def test_get_tests_returns_none_for_an_unknown_exercise() -> None:
    catalog = AsyncMock()
    catalog.get_exercise.side_effect = ValueError("Exercise nope not found in lesson basics")
    service = LessonService(catalog, AsyncMock(), MagicMock())

    assert await service.get_tests("basics", "nope") is None


async def test_get_lessons_with_no_lessons_is_empty() -> None:
    catalog = AsyncMock()
    catalog.get_lessons.return_value = {}
    progress = AsyncMock()
    progress.count_completed_by_lesson.return_value = {}

    assert await LessonService(catalog, progress, MagicMock()).get_lessons(4) == []
