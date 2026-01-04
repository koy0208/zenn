from sqlalchemy.orm import Session
from app.domain.model.article import Article
from app.domain.repository.article_repository import ArticleRepository
from app.adapter.orm.model import ArticleORM


class SQLAlchemyArticleRepository(ArticleRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, article: Article) -> Article:
        article_orm = ArticleORM.from_domain(article)

        if article.id:
            # 更新の場合（今回は簡易的にマージ）
            article_orm = self.db.merge(article_orm)
        else:
            # 新規作成
            self.db.add(article_orm)

        self.db.commit()
        self.db.refresh(article_orm)
        return article_orm.to_domain()

    def find_by_id(self, article_id: int) -> Article | None:
        article_orm = (
            self.db.query(ArticleORM).filter(ArticleORM.id == article_id).first()
        )
        if article_orm:
            return article_orm.to_domain()
        return None

    def find_all(self) -> list[Article]:
        article_orms = self.db.query(ArticleORM).all()
        return [article_orm.to_domain() for article_orm in article_orms]

    def delete(self, article_id: int) -> None:
        article_orm = (
            self.db.query(ArticleORM).filter(ArticleORM.id == article_id).first()
        )
        if article_orm:
            self.db.delete(article_orm)
            self.db.commit()
        return None
