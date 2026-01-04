from app.domain.model.article import Article
from app.domain.repository.article_repository import ArticleRepository
from app.usecase.dto.article_dto import ArticleCreateInput, ArticleOutput


class CreateArticleUseCase:
    def __init__(self, repository: ArticleRepository):
        self.repository = repository

    def execute(self, input_data: ArticleCreateInput) -> ArticleOutput:
        # DTOからドメインモデルへ変換
        article = input_data.to_domain()

        saved_article = self.repository.save(article)

        return ArticleOutput.from_domain(saved_article)
