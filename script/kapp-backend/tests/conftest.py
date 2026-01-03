import sys
import os

# プロジェクトルートをsys.pathに追加 (testsディレクトリの1つ上)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

"""
テストの実行例:
1. 通常のユニットテスト (Mock使用)
   uv run pytest

2. 統合テスト (実際のAWS環境を使用)
   export RUN_INTEGRATION=1
   export TEST_S3_BUCKET_NAME=your-bucket-name
   export AWS_PROFILE=your-profile
   uv run pytest -m integration
"""

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
