from app.domain.model.article import Article
from pydantic import BaseModel


class ArticleCreateInput(BaseModel):
    title: str
    content: str
    author_id: int

    def to_domain(self) -> Article:
        return Article(
            title=self.title,
            content=self.content,
            author_id=self.author_id,
        )


class ArticleUpdateInput(BaseModel):
    title: str | None = None
    content: str | None = None

    def apply_to_domain(self, article: Article) -> Article:
        if self.title is not None:
            article.title = self.title
        if self.content is not None:
            article.content = self.content
        return article


class ArticleOutput(BaseModel):
    id: int
    title: str
    content: str
    author_id: int

    @classmethod
    def from_domain(cls, domain_model: Article) -> "ArticleOutput":
        return cls(
            id=domain_model.id,
            title=domain_model.title,
            content=domain_model.content,
            author_id=domain_model.author_id,
        )
