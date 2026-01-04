from typing import Protocol
from app.domain.model.user import User

class UserRepository(Protocol):
    def save(self, user: User) -> User:
        ...

    def find_by_email(self, email: str) -> User | None:
        ...

    def find_by_username(self, username: str) -> User | None:
        ...