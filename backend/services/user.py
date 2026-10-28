import bcrypt
from database.types.user import User, UserRepository

class UserService:
    def __init__(self, user_repository: UserRepository | None = None):
        self.user_repository = user_repository or UserRepository()

    def _hash_password(self, password: str) -> str:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    async def authenticate_user(self, attempted_username: str, attempted_password: str) -> User | None:
        attempted_hashed_password = self._hash_password(attempted_password)

        try:
            user = await self.user_repository.get_user_by_login(attempted_username, attempted_hashed_password)
            return user
        except ValueError:
            return None
