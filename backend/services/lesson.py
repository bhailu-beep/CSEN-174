from starlette.concurrency import run_in_threadpool

from database.types.lesson import Exercise, LessonOverview, LessonRepository, TestCase
from database.types.lesson_progress import LessonProgressRepository
from models.result import SubmissionResult, submission_result
from services.cpp_runner import CppRunnerService


class LessonService:
    def __init__(
        self,
        lesson_repository: LessonRepository,
        lesson_progress_repository: LessonProgressRepository,
        runner: CppRunnerService,
    ):
        self.lesson_repository = lesson_repository
        self.lesson_progress_repository = lesson_progress_repository
        self.runner = runner

    async def get_lessons(self, user_id: int) -> list[LessonOverview]:
        catalog = await self.lesson_repository.get_lessons()
        completed = await self.lesson_progress_repository.count_completed_by_lesson(user_id)
        return [
            LessonOverview(
                id=lesson.id,
                name=lesson.name,
                exercise_count=len(exercises),
                completed_count=completed.get(lesson.id, 0),
            )
            for lesson, exercises in catalog.items()
        ]

    async def get_exercise(self, lesson_id: str, exercise_id: str) -> Exercise:
        return await self.lesson_repository.get_exercise(lesson_id, exercise_id)

    async def run_code(self, user_id: int, lesson_id: str, exercise_id: str, code: str) -> SubmissionResult:
        exercise = await self.lesson_repository.get_exercise(lesson_id, exercise_id)
        result = await run_in_threadpool(
            self.runner.run,
            code,
            tester=exercise.tester_code,
            tests=exercise.tests,
        )
        submission = submission_result(result)
        if submission.status == "passed":
            await self.lesson_progress_repository.mark_completed(user_id, lesson_id, exercise_id)
        return submission

    async def get_tests(self, lesson_id: str, exercise_id: str) -> list[TestCase] | None:
        try:
            exercise = await self.lesson_repository.get_exercise(lesson_id, exercise_id)
        except ValueError:
            return None
        return exercise.tests
