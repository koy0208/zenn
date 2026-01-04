from app.domain.repository.article_repository import ArticleRepository
from app.usecase.dto.article_dto import ArticleOutput

class ListArticlesUseCase:
    def __init__(self, repository: ArticleRepository):
        self.repository = repository

    def execute(self) -> list[ArticleOutput]:
        articles = self.repository.find_all()
        return [ArticleOutput.from_domain(a) for a in articles]
