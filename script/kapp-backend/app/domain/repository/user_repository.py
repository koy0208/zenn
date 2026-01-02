from abc import ABC, abstractmethod
from app.domain.model.user import User

class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def find_by_username(self, username: str) -> User | None:
        pass