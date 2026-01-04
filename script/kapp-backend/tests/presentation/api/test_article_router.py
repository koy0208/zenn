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


def test_update_article_success(client: TestClient, db: Session):
    # 1. Prepare: Create a user and an article
    user = UserORM(
        username="update_author",
        email="update_author@example.com",
        hashed_password="hashed_secret",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    article = ArticleORM(
        title="Original Title",
        content="Original Content",
        author_id=user.id
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    # 2. Execute: Call Update API
    response = client.put(
        f"/articles/{article.id}",
        json={
            "title": "Updated Title",
            "content": "Updated Content"
        },
    )

    # 3. Verify Response
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"
    assert data["id"] == article.id

    # 4. Verify DB
    db.refresh(article)
    assert article.title == "Updated Title"
    assert article.content == "Updated Content"


def test_update_article_partial_update(client: TestClient, db: Session):
    # 1. Prepare
    user = UserORM(
        username="partial_author",
        email="partial_author@example.com",
        hashed_password="hashed_secret",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    article = ArticleORM(
        title="Original Title",
        content="Original Content",
        author_id=user.id
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    # 2. Execute: Update only title
    response = client.put(
        f"/articles/{article.id}",
        json={
            "title": "New Title"
        },
    )

    # 3. Verify
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["content"] == "Original Content"  # Should remain unchanged


def test_update_article_not_found(client: TestClient, db: Session):
    response = client.put(
        "/articles/99999",
        json={
            "title": "Ghost Article",
            "content": "This should fail"
        },
    )
    assert response.status_code == 404