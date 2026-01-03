from sqlmodel import Field
from app.adapter.orm.base_orm import BaseORM
from app.domain.model.user import User as UserDomain

class UserORM(BaseORM, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True, index=True)
    username: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)

    # ドメインモデルへの変換メソッド
    def to_domain(self) -> UserDomain:
        return UserDomain(
            id=self.id,
            username=self.username,
            email=self.email,
            hashed_password=self.hashed_password,
        )

    # ドメインモデルからの変換メソッド (クラスメソッド)
    @classmethod
    def from_domain(cls, user: UserDomain) -> "UserORM":
        return cls(
            id=user.id,
            username=user.username,
            email=str(user.email),
            hashed_password=user.hashed_password,
        )