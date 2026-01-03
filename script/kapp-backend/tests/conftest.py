import os
import pytest

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
