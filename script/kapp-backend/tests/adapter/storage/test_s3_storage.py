import pytest
from moto import mock_aws
import boto3
from app.adapter.storage.s3_storage import S3Storage
from app.config import settings

@pytest.fixture
def s3_setup():
    with mock_aws():
        # テスト用の仮想S3環境を構築
        s3 = boto3.client("s3", region_name="ap-northeast-1")
        bucket_name = "test-bucket"
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "ap-northeast-1"}
        )
        
        # テストデータを投入
        s3.put_object(Bucket=bucket_name, Key="test.txt", Body=b"hello s3")
        
        yield s3, bucket_name

def test_get_file_success(s3_setup, monkeypatch):
    _, bucket_name = s3_setup
    
    # 設定をテスト用バケットに書き換え
    monkeypatch.setattr(settings, "S3_BUCKET_NAME", bucket_name)
    
    storage = S3Storage()
    content = storage.get_file("test.txt")
    
    assert content == b"hello s3"

def test_get_file_not_found(s3_setup, monkeypatch):
    _, bucket_name = s3_setup
    monkeypatch.setattr(settings, "S3_BUCKET_NAME", bucket_name)
    
    storage = S3Storage()
    
    with pytest.raises(FileNotFoundError):
        storage.get_file("non-existent.txt")
