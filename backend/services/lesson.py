from database.types.lesson import Lesson, LessonRepository


class LessonService:
    def __init__(self, lesson_repository: LessonRepository):
        self.lesson_repository = lesson_repository

    async def get_lesson(self, chapter_id: int, lesson_id: int) -> Lesson:
        return await self.lesson_repository.get_lesson(chapter_id, lesson_id)

    async def get_solution(self, chapter_id: int, lesson_id: int) -> str:
        return await self.lesson_repository.get_solution(chapter_id, lesson_id)
