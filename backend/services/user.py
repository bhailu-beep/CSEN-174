import asyncio
from datetime import datetime, timedelta, timezone
from typing import Literal, NamedTuple

import bcrypt
import jwt
from decouple import config
from database.types.user import User, UserRepository

ACCESS_TOKEN_TTL_SECONDS = 15 * 60  # 15 minutes
REFRESH_TOKEN_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days
_JWT_ALGORITHM = "HS256"
_DUMMY_PASSWORD_HASH = bcrypt.hashpw(b"password", bcrypt.gensalt())

TokenType = Literal["access", "refresh"]


class TokenPair(NamedTuple):
    access_token: str
    refresh_token: str


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def _hash_password(self, password: str) -> str:
        def hash_password() -> str:
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode('utf-8')

        return await asyncio.to_thread(hash_password)

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
            # for security reasons, we don't want to leak information about the existence of the user.
            # so we do a fake password check to prevent timing attacks
            await asyncio.to_thread(self._password_matches, attempted_password, _DUMMY_PASSWORD_HASH)
            return None
        if not await asyncio.to_thread(self._password_matches, attempted_password, user.hashed_password):
            return None
        return user

    def _issue_token(self, user: User, token_type: TokenType, ttl_seconds: int) -> str:
        expires = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        return jwt.encode(
            {
                "sub": str(user.id),
                "username": user.username,
                "type": token_type,
                "exp": expires,
            },
            config('JWT_SECRET'),
            algorithm=_JWT_ALGORITHM,
        )

    def _issue_token_pair(self, user: User) -> TokenPair:
        return TokenPair(
            access_token=self._issue_token(user, "access", ACCESS_TOKEN_TTL_SECONDS),
            refresh_token=self._issue_token(user, "refresh", REFRESH_TOKEN_TTL_SECONDS),
        )

    async def login(self, username: str, password: str) -> TokenPair | None:
        user = await self.authenticate_user(username, password)
        if user is None:
            return None
        return self._issue_token_pair(user)

    async def create_user(self, username: str, password: str) -> TokenPair | None:
        hashed_password = await self._hash_password(password)
        user = await self.user_repository.create_user(username, hashed_password)
        return self._issue_token_pair(user)

    async def refresh(self, refresh_token: str) -> TokenPair | None:
        user = await self.user_from_token(refresh_token, expected_type="refresh")
        if user is None:
            return None
        return self._issue_token_pair(user)

    async def user_from_token(
        self,
        token: str,
        *,
        expected_type: TokenType = "access",
    ) -> User | None:
        try:
            payload = jwt.decode(token, config('JWT_SECRET'), algorithms=[_JWT_ALGORITHM])
        except jwt.PyJWTError:
            return None
        if payload.get("type") != expected_type:
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
