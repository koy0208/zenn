from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.adapter.orm.model import UserORM, ArticleORM


def test_create_article(client: TestClient, db: Session):
    # 1. 準備: 記事の投稿者となるユーザーを作成
    user = UserORM(
        username="article_author",
        email="author@example.com",
        hashed_password="hashed_secret",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 2. 実行: APIを叩く
    response = client.post(
        "/articles/",
        json={
            "title": "My First Article",
            "content": "This is the content of the article.",
            "author_id": user.id,
        },
    )

    # 3. 検証: レスポンス
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My First Article"
    assert data["content"] == "This is the content of the article."
    assert data["author_id"] == user.id
    assert "id" in data

    # 4. 検証: DBに保存されているか直接確認
    article_in_db = db.query(ArticleORM).filter(ArticleORM.id == data["id"]).first()
    assert article_in_db is not None
    assert article_in_db.title == "My First Article"
    assert article_in_db.author_id == user.id
