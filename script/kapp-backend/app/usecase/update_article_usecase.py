from app.domain.repository.article_repository import ArticleRepository
from app.usecase.dto.article_dto import ArticleUpdateInput, ArticleOutput

class UpdateArticleUseCase:
    def __init__(self, repository: ArticleRepository):
        self.repository = repository

    def execute(self, article_id: int, input_data: ArticleUpdateInput) -> ArticleOutput:
        article = self.repository.find_by_id(article_id)
        if not article:
            raise ValueError(f"Article with id {article_id} not found")
        
        updated_article = input_data.apply_to_domain(article)
        saved_article = self.repository.save(updated_article)
        
        return ArticleOutput.from_domain(saved_article)
