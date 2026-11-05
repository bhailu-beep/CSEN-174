from database.types.lesson import Exercise, LessonRepository


class LessonService:
    def __init__(self, lesson_repository: LessonRepository):
        self.lesson_repository = lesson_repository

    async def get_exercise(self, lesson_id: str, exercise_id: str) -> Exercise:
        return await self.lesson_repository.get_exercise(lesson_id, exercise_id)
