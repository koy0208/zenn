from typing import Protocol

class FileStorage(Protocol):
    def get_file(self, key: str) -> bytes:
        ...
    
    def put_file(self, key: str, data: bytes) -> None:
        ...

    def exists(self, key: str) -> bool:
        ...
