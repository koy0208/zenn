from app.domain.repository.article_repository import ArticleRepository
from app.usecase.dto.article_dto import ArticleOutput

class GetArticleUseCase:
    def __init__(self, repository: ArticleRepository):
        self.repository = repository

    def execute(self, article_id: int) -> ArticleOutput:
        article = self.repository.find_by_id(article_id)
        if not article:
            raise ValueError(f"Article with id {article_id} not found")
        return ArticleOutput.from_domain(article)
