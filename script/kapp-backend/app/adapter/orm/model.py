from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from app.domain.model.user import User as UserDomain
from app.domain.model.article import Article as ArticleDomain


class BaseORM(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UserORM(BaseORM, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True, index=True)
    username: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    articles: list["ArticleORM"] = Relationship(back_populates="author")

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


class ArticleORM(BaseORM, table=True):
    __tablename__ = "articles"

    id: int | None = Field(default=None, primary_key=True, index=True)
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    author_id: int = Field(foreign_key="users.id", nullable=False, index=True)

    # リレーション (文字列で型指定することで循環参照を回避)
    author: "UserORM" = Relationship(back_populates="articles")

    # ドメインモデルへの変換メソッド
    def to_domain(self) -> ArticleDomain:
        return ArticleDomain(
            id=self.id,
            title=self.title,
            content=self.content,
            author_id=self.author_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    # ドメインモデルからの変換メソッド (クラスメソッド)
    @classmethod
    def from_domain(cls, article: ArticleDomain) -> "ArticleORM":
        return cls(
            id=article.id,
            title=article.title,
            content=article.content,
            author_id=article.author_id,
        )
