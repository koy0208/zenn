from sqlalchemy import Column, Integer, String
from app.adapter.database import Base
from app.domain.model.user import User as UserDomain


class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # ドメインモデルへの変換メソッド
    def to_domain(self) -> UserDomain:
        return UserDomain(
            id=self.id,
            username=self.username,
            email=self.email,
            hashed_password=self.hashed_password,
        )

    # ドメインモデルからの変換メソッド (静的メソッド)
    @staticmethod
    def from_domain(user: UserDomain) -> "UserORM":
        return UserORM(
            id=user.id,
            username=user.username,
            email=str(user.email),  # EmailStr -> str
            hashed_password=user.hashed_password,
        )
