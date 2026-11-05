from asyncpg import Connection


class LessonProgressRepository:
    def __init__(self, connection: Connection):
        self.connection = connection

    async def create_lesson_progress(self, user_id: int, lesson_id: str, exercise_id: str, code: str) -> None:
        await self.connection.execute(
            "INSERT INTO lesson_progress (user_id, lesson_id, exercise_id, code) VALUES ($1, $2, $3, $4)",
            user_id,
            lesson_id,
            exercise_id,
            code,
        )

    async def get_code(self, user_id: int, lesson_id: str, exercise_id: str) -> str | None:
        result = await self.connection.fetchrow(
            "SELECT code FROM lesson_progress WHERE user_id = $1 AND lesson_id = $2 AND exercise_id = $3",
            user_id,
            lesson_id,
            exercise_id,
        )
        return result["code"] if result else None

    async def update_code(self, user_id: int, lesson_id: str, exercise_id: str, code: str) -> None:
        await self.connection.execute(
            "UPDATE lesson_progress SET code = $1 WHERE user_id = $2 AND lesson_id = $3 AND exercise_id = $4",
            code,
            user_id,
            lesson_id,
            exercise_id,
        )

    async def mark_completed(self, user_id: int, lesson_id: str, exercise_id: str) -> None:
        await self.connection.execute(
            "UPDATE lesson_progress SET completed = TRUE WHERE user_id = $1 AND lesson_id = $2 AND exercise_id = $3",
            user_id,
            lesson_id,
            exercise_id,
        )

    async def clear_all_progress(self, user_id: int) -> None:
        await self.connection.execute(
            "DELETE FROM lesson_progress WHERE user_id = $1",
            user_id,
        )
