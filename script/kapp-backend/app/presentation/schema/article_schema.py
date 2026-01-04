from pydantic import BaseModel
from app.usecase.dto.article_dto import ArticleOutput


class ArticleCreateRequest(BaseModel):
    title: str
    content: str
    author_id: int


class ArticleUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None


class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int

    @classmethod
    def from_dto(cls, dto: "ArticleOutput") -> "ArticleResponse":
        return cls(
            id=dto.id,
            title=dto.title,
            content=dto.content,
            author_id=dto.author_id,
        )
