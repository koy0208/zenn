from app.domain.repository.article_repository import ArticleRepository

class DeleteArticleUseCase:
    def __init__(self, repository: ArticleRepository):
        self.repository = repository

    def execute(self, article_id: int) -> None:
        article = self.repository.find_by_id(article_id)
        if not article:
            raise ValueError(f"Article with id {article_id} not found")
        
        self.repository.delete(article_id)
