from app.domain.repository.file_storage import FileStorage
from app.adapter.storage.s3_storage import S3Storage

def get_file_storage() -> FileStorage:
    # 実際の実装（S3Storage）を返す
    # 将来的にローカルストレージやMockに切り替えるのもここ一箇所で可能
    return S3Storage()
