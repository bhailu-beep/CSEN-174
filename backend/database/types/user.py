from asyncpg import Connection
from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    hashed_password: str

class UserRepository:
    def __init__(self, connection: Connection):
        self.connection = connection

    async def create_user(self, username: str, hashed_password: str) -> User:
        user_id = await self.connection.fetchval(
            "INSERT INTO users (username, hashed_password) VALUES ($1, $2) RETURNING id",
            username,
            hashed_password
        )
        return User(id=user_id, username=username, hashed_password=hashed_password)

    async def get_user_by_id(self, id: int) -> User:
        result = await self.connection.fetchrow(
            "SELECT id, username, hashed_password FROM users WHERE id = $1",
            id
        )
        if result is None:
            raise ValueError(f"User with id {id} not found")
        return User(id=result['id'], username=result['username'], hashed_password=result['hashed_password'])

    async def get_user_by_username(self, username: str) -> User:
        result = await self.connection.fetchrow(
            "SELECT id, username, hashed_password FROM users WHERE username = $1",
            username
        )
        if result is None:
            raise ValueError(f"User {username} not found")
        return User(id=result['id'], username=result['username'], hashed_password=result['hashed_password'])

    async def get_user_by_login(self, username: str, hashed_password: str) -> User:
        result = await self.connection.fetchrow(
            "SELECT id, username, hashed_password FROM users WHERE username = $1 AND hashed_password = $2",
            username,
            hashed_password
        )
        if result is None:
            raise ValueError(f"User, hashed password ({username}, {hashed_password}) not found")
        return User(id=result['id'], username=result['username'], hashed_password=result['hashed_password'])
