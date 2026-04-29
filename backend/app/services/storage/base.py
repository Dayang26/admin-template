from typing import Protocol

from fastapi import UploadFile
from sqlmodel import SQLModel


class StoredFile(SQLModel):
    storage_provider: str
    storage_key: str
    public_url: str | None
    size_bytes: int
    sha256: str


class StorageProvider(Protocol):
    def save(
        self,
        *,
        file: UploadFile,
        visibility: str,
        extension: str,
        max_size_bytes: int,
    ) -> StoredFile: ...

    def delete(self, *, visibility: str, storage_key: str) -> None: ...
