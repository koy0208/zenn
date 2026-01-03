from abc import ABC, abstractmethod

class FileStorage(ABC):
    @abstractmethod
    def get_file(self, key: str) -> bytes:
        """指定されたキーのファイル内容をバイト列として取得する"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """指定されたキーのファイルが存在するか確認する"""
        pass
