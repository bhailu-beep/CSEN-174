from database.types.lesson import LessonRepository
from database.types.lesson_progress import LessonProgressRepository


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

    async def clear_all_progress(self, user_id: int):
        await self.lesson_progress_repository.clear_all_progress(user_id)

    async def _require_exercise(self, lesson_id: str, exercise_id: str) -> None:
        await self.lesson_repository.get_exercise(lesson_id, exercise_id)
