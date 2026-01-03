import boto3
from botocore.exceptions import ClientError
from app.domain.repository.file_storage import FileStorage
from app.config import settings

class S3Storage(FileStorage):
    def __init__(self):
        # 認証情報はAWS標準チェーン（SSOプロファイル、環境変数、IAMロール）から自動取得
        self.s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    def get_file(self, key: str) -> bytes:
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response["Body"].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"File not found: {key}")
            raise e

    def exists(self, key: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise e
