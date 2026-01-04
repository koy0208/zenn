from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.adapter.database import get_db
from app.adapter.repository.sqlalchemy_article_repository import SQLAlchemyArticleRepository
from app.usecase.create_article_usecase import CreateArticleUseCase
from app.usecase.get_article_usecase import GetArticleUseCase
from app.usecase.list_articles_usecase import ListArticlesUseCase
from app.usecase.update_article_usecase import UpdateArticleUseCase
from app.usecase.delete_article_usecase import DeleteArticleUseCase
from app.usecase.dto.article_dto import ArticleCreateInput, ArticleUpdateInput
from app.presentation.schema.article_schema import ArticleCreateRequest, ArticleUpdateRequest, ArticleResponse

router = APIRouter(prefix="/articles", tags=["articles"])

# DI用ユーティリティ
def get_repository(db: Session = Depends(get_db)):
    return SQLAlchemyArticleRepository(db)

@router.post("/", response_model=ArticleResponse)
def create_article(
    request: ArticleCreateRequest,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    usecase = CreateArticleUseCase(get_repository(db))
    input_data = ArticleCreateInput(
        title=request.title, content=request.content, author_id=request.author_id
    )
    output = usecase.execute(input_data)
    return ArticleResponse.from_dto(output)

@router.get("/", response_model=list[ArticleResponse])
def list_articles(
    db: Session = Depends(get_db),
) -> list[ArticleResponse]:
    usecase = ListArticlesUseCase(get_repository(db))
    outputs = usecase.execute()
    return [ArticleResponse.from_dto(o) for o in outputs]

@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    usecase = GetArticleUseCase(get_repository(db))
    try:
        output = usecase.execute(article_id)
        return ArticleResponse.from_dto(output)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: int,
    request: ArticleUpdateRequest,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    usecase = UpdateArticleUseCase(get_repository(db))
    input_data = ArticleUpdateInput(title=request.title, content=request.content)
    try:
        output = usecase.execute(article_id, input_data)
        return ArticleResponse.from_dto(output)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{article_id}", status_code=204)
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
):
    usecase = DeleteArticleUseCase(get_repository(db))
    try:
        usecase.execute(article_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))