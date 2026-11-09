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
            """
            INSERT INTO lesson_progress (user_id, lesson_id, exercise_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, lesson_id, exercise_id)
            DO UPDATE SET code = lesson_progress.code
            RETURNING code
            """,
            user_id,
            lesson_id,
            exercise_id,
        )
        return result["code"]

    async def update_code(self, user_id: int, lesson_id: str, exercise_id: str, code: str) -> None:
        await self.connection.execute(
            """
            INSERT INTO lesson_progress (user_id, lesson_id, exercise_id, code)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id, lesson_id, exercise_id)
            DO UPDATE SET code = EXCLUDED.code
            """,
            user_id,
            lesson_id,
            exercise_id,
            code,
        )

    async def mark_completed(self, user_id: int, lesson_id: str, exercise_id: str) -> None:
        await self.connection.execute(
            """
            INSERT INTO lesson_progress (user_id, lesson_id, exercise_id, completed)
            VALUES ($1, $2, $3, TRUE)
            ON CONFLICT (user_id, lesson_id, exercise_id)
            DO UPDATE SET completed = TRUE
            """,
            user_id,
            lesson_id,
            exercise_id,
        )

    async def count_completed_by_lesson(self, user_id: int) -> dict[str, int]:
        rows = await self.connection.fetch(
            """
            SELECT lesson_id, COUNT(*) AS completed
            FROM lesson_progress
            WHERE user_id = $1 AND completed
            GROUP BY lesson_id
            """,
            user_id,
        )
        return {row["lesson_id"]: row["completed"] for row in rows}

    async def clear_all_progress(self, user_id: int) -> None:
        await self.connection.execute(
            "DELETE FROM lesson_progress WHERE user_id = $1",
            user_id,
        )
