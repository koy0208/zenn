import os
import pytest
import boto3
import uuid
from app.adapter.storage.s3_storage import S3Storage
from app.config import settings

# 統合テストであることをマーク
@pytest.mark.integration
class TestS3StorageIntegration:
    
    @pytest.fixture(scope="class")
    def real_bucket_name(self):
        bucket = os.getenv("TEST_S3_BUCKET_NAME")
        if not bucket:
            pytest.skip("TEST_S3_BUCKET_NAME environment variable not set")
        return bucket

    @pytest.fixture(scope="class")
    def s3_client(self):
        # 実際のAWSクライアント
        return boto3.client("s3")

    def test_upload_and_get_real_file(self, real_bucket_name, s3_client, monkeypatch):
        """実際のS3にアップロードして取得できるか確認"""
        
        # 設定をテスト対象のバケットに向ける
        monkeypatch.setattr(settings, "S3_BUCKET_NAME", real_bucket_name)
        
        # テストデータの準備
        test_key = f"integration-test-{uuid.uuid4()}.txt"
        test_body = b"Hello from Real S3 Integration Test"
        
        try:
            # 1. 直接S3にアップロード (前提条件作り)
            s3_client.put_object(Bucket=real_bucket_name, Key=test_key, Body=test_body)
            
            # 2. アプリのS3Storage経由で取得
            storage = S3Storage()
            content = storage.get_file(test_key)
            
            # 3. 検証
            assert content == test_body
            
        finally:
            # 4. 後片付け (必ず消す)
            try:
                s3_client.delete_object(Bucket=real_bucket_name, Key=test_key)
            except:
                pass

    def test_real_file_exists(self, real_bucket_name, s3_client, monkeypatch):
        monkeypatch.setattr(settings, "S3_BUCKET_NAME", real_bucket_name)
        storage = S3Storage()
        
        # 存在しないファイルの確認
        assert storage.exists(f"non-existent-{uuid.uuid4()}") is False
