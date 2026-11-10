from database.types.lesson import LessonRepository
from database.types.lesson_progress import ExerciseProgress, LessonProgressRepository


class LessonProgressService:
    def __init__(
        self,
        lesson_progress_repository: LessonProgressRepository,
        lesson_repository: LessonRepository,
    ):
        self.lesson_progress_repository = lesson_progress_repository
        self.lesson_repository = lesson_repository

    async def create_lesson_progress(self, user_id: int, lesson_id: str, exercise_id: str, code: str):
        await self._require_exercise(lesson_id, exercise_id)
        await self.lesson_progress_repository.create_lesson_progress(user_id, lesson_id, exercise_id, code)

    async def get_code(self, user_id: int, lesson_id: str, exercise_id: str) -> str | None:
        await self._require_exercise(lesson_id, exercise_id)
        return await self.lesson_progress_repository.get_code(user_id, lesson_id, exercise_id)

    async def update_code(self, user_id: int, lesson_id: str, exercise_id: str, code: str):
        await self._require_exercise(lesson_id, exercise_id)
        await self.lesson_progress_repository.update_code(user_id, lesson_id, exercise_id, code)

    async def mark_completed(self, user_id: int, lesson_id: str, exercise_id: str):
        await self._require_exercise(lesson_id, exercise_id)
        await self.lesson_progress_repository.mark_completed(user_id, lesson_id, exercise_id)

    async def get_lesson_progress(self, user_id: int, lesson_id: str) -> list[ExerciseProgress]:
        """Every exercise in the lesson, in catalog order. Exercises with no saved row are not started."""
        catalog = await self.lesson_repository.get_lessons()
        exercises = next((items for lesson, items in catalog.items() if lesson.id == lesson_id), None)
        if exercises is None:
            raise ValueError(f"Lesson {lesson_id} not found")
        saved = {
            row.exercise_id: row
            for row in await self.lesson_progress_repository.get_lesson_progress(user_id, lesson_id)
        }
        return [
            saved.get(exercise.id, ExerciseProgress(exercise_id=exercise.id, completed=False, started=False))
            for exercise in exercises
        ]

    async def clear_all_progress(self, user_id: int):
        await self.lesson_progress_repository.clear_all_progress(user_id)

    async def _require_exercise(self, lesson_id: str, exercise_id: str) -> None:
        await self.lesson_repository.get_exercise(lesson_id, exercise_id)
