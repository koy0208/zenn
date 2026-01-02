from app.domain.model.user import User
from app.domain.repository.user_repository import UserRepository

class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self.users: list[User] = []
        self._id_counter = 1

    def save(self, user: User) -> User:
        if user.id is None:
            user.id = self._id_counter
            self._id_counter += 1
        
        # 既存ユーザーの更新または新規追加
        self.users = [u for u in self.users if u.id != user.id]
        self.users.append(user)
        return user

    def find_by_email(self, email: str) -> User | None:
        return next((u for u in self.users if u.email == email), None)

    def find_by_username(self, username: str) -> User | None:
        return next((u for u in self.users if u.username == username), None)