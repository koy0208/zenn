import sys
import os

# プロジェクトルートをsys.pathに追加 (testsディレクトリの1つ上)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import tempfile
from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.adapter.database import get_db
from app.adapter.orm.model import UserORM, ArticleORM  # Ensure models are loaded


@pytest.fixture()
def db():
    """テスト用のデータベースセッションを提供"""
    # 一時ファイルを作成
    fd, path = tempfile.mkstemp()
    db_url = f"sqlite:///{path}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    SQLModel.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        SQLModel.metadata.drop_all(bind=engine)
        engine.dispose()
        os.close(fd)
        if os.path.exists(path):
            os.remove(path)


@pytest.fixture()
def client(db: Session):
    """テスト用のAPIクライアントを提供（DBをテスト用DBに差し替える）"""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    # 統合テスト実行時はモック設定をスキップする
    if os.getenv("RUN_INTEGRATION"):
        return

    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "ap-northeast-1"
    # AWS_PROFILEが残っているとエラーになるため削除
    if "AWS_PROFILE" in os.environ:
        del os.environ["AWS_PROFILE"]
