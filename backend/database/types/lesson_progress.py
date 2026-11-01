from asyncpg import Connection

class LessonProgressRepository:
    def __init__(self, connection: Connection):
        self.connection = connection

    async def create_lesson_progress(self, user_id: int, chapter_id: int, lesson_id: int, code: str) -> None:
        await self.connection.execute(
            "INSERT INTO lesson_progress (user_id, chapter_id, lesson_id, code) VALUES ($1, $2, $3, $4)",
            user_id,
            chapter_id,
            lesson_id,
            code
        )

    async def get_code(self, user_id: int, chapter_id: int, lesson_id: int) -> str | None:
        result = await self.connection.fetchrow(
            "SELECT code FROM lesson_progress WHERE user_id = $1 AND chapter_id = $2 AND lesson_id = $3",
            user_id,
            chapter_id,
            lesson_id
        )
        return result['code'] if result else None

    async def update_code(self, user_id: int, chapter_id: int, lesson_id: int, code: str) -> None:
        await self.connection.execute(
            "UPDATE lesson_progress SET code = $1 WHERE user_id = $2 AND chapter_id = $3 AND lesson_id = $4",
            code,
            user_id,
            chapter_id,
            lesson_id
        )

    async def mark_completed(self, user_id: int, chapter_id: int, lesson_id: int) -> None:
        await self.connection.execute(
            "UPDATE lesson_progress SET completed = TRUE WHERE user_id = $1 AND chapter_id = $2 AND lesson_id = $3",
            user_id,
            chapter_id,
            lesson_id
        )

    async def clear_all_progress(self, user_id: int) -> None:
        await self.connection.execute(
            "DELETE FROM lesson_progress WHERE user_id = $1",
            user_id
        )
