import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel


class UploadVisibility(str, Enum):
    public = "public"
    private = "private"


class UploadFileType(str, Enum):
    image = "image"


class UploadFileResp(SQLModel):
    id: uuid.UUID
    original_filename: str
    content_type: str
    size_bytes: int
    file_type: str
    visibility: str
    storage_provider: str
    storage_key: str
    public_url: str | None
    purpose: str | None
    created_at: datetime
