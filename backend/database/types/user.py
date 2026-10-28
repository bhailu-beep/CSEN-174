from pydantic import BaseModel

from database.connection import DbConnection


class User(BaseModel):
    id: int
    username: str
    hashed_password: str

class UserRepository:
    async def create_user(self, username: str, hashed_password: str) -> User:
        async with DbConnection.pool.acquire() as conn:
            user_id = await conn.fetchval(
                "INSERT INTO users (username, hashed_password) VALUES ($1, $2) RETURNING id",
                username,
                hashed_password
            )
            return User(id=user_id, username=username, hashed_password=hashed_password)

    async def get_user_by_id(self, id: int) -> User:
        async with DbConnection.pool.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT id, username, hashed_password FROM users WHERE id = $1",
                id
            )
            if result is None:
                raise ValueError(f"User with id {id} not found")
            return User(id=result['id'], username=result['username'], hashed_password=result['hashed_password'])
