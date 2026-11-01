from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from decouple import config
from database.types.user import User, UserRepository

ACCESS_TOKEN_TTL_SECONDS = 7 * 24 * 60 * 60
_JWT_ALGORITHM = "HS256"
_DUMMY_PASSWORD_HASH = bcrypt.hashpw(b"password", bcrypt.gensalt())

class UserService:
    def __init__(self, user_repository: UserRepository | None = None):
        self.user_repository = user_repository or UserRepository()

    def _hash_password(self, password: str) -> str:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    def _password_matches(self, password: str, hashed_password: str | bytes) -> bool:
        hashed_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_bytes)
        except ValueError:
            return False

    async def authenticate_user(self, attempted_username: str, attempted_password: str) -> User | None:
        try:
            user = await self.user_repository.get_user_by_username(attempted_username)
        except ValueError:
            self._password_matches(attempted_password, _DUMMY_PASSWORD_HASH)
            return None
        if not self._password_matches(attempted_password, user.hashed_password):
            return None
        return user

    def _issue_token(self, user: User) -> str:
        expires = datetime.now(timezone.utc) + timedelta(seconds=ACCESS_TOKEN_TTL_SECONDS)
        token = jwt.encode(
            {"sub": str(user.id), "username": user.username, "exp": expires},
            config('JWT_SECRET'),
            algorithm=_JWT_ALGORITHM,
        )
        return token

    async def login(self, username: str, password: str) -> str | None:
        user = await self.authenticate_user(username, password)
        if user is None:
            return None
        return self._issue_token(user)

    async def user_from_token(self, token: str) -> User | None:
        try:
            payload = jwt.decode(token, config('JWT_SECRET'), algorithms=[_JWT_ALGORITHM])
        except jwt.PyJWTError:
            return None
        subject = payload.get("sub")
        if not isinstance(subject, str):
            return None
        try:
            user_id = int(subject)
        except ValueError:
            return None
        try:
            return await self.user_repository.get_user_by_id(user_id)
        except ValueError:
            return None
