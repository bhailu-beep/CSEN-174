from database.types.lesson_progress import LessonProgressRepository

class LessonProgressService:
    def __init__(self, lesson_progress_repository: LessonProgressRepository):
        self.lesson_progress_repository = lesson_progress_repository

    async def create_lesson_progress(self, user_id: int, chapter_id: int, lesson_id: int, code: str):
        await self.lesson_progress_repository.create_lesson_progress(user_id, chapter_id, lesson_id, code)

    async def get_code(self, user_id: int, chapter_id: int, lesson_id: int):
        return await self.lesson_progress_repository.get_code(user_id, chapter_id, lesson_id)

    async def update_code(self, user_id: int, chapter_id: int, lesson_id: int, code: str):
        await self.lesson_progress_repository.update_code(user_id, chapter_id, lesson_id, code)

    async def mark_completed(self, user_id: int, chapter_id: int, lesson_id: int):
        await self.lesson_progress_repository.mark_completed(user_id, chapter_id, lesson_id)

    async def clear_all_progress(self, user_id: int):
        await self.lesson_progress_repository.clear_all_progress(user_id)
