import uuid
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.db.base import TimestampMixin, UUIDPrimaryKeyMixin


class UploadFile(UUIDPrimaryKeyMixin, TimestampMixin, SQLModel, table=True):
    __tablename__ = "t_upload_file" # type: ignore

    original_filename: str = Field(max_length=255)
    stored_filename: str = Field(max_length=255)
    extension: str = Field(max_length=50)
    content_type: str = Field(max_length=100)
    size_bytes: int
    sha256: str = Field(max_length=64)
    file_type: str = Field(max_length=50)  # image
    visibility: str = Field(max_length=50)  # public / private
    storage_provider: str = Field(max_length=50)  # local
    storage_key: str = Field(max_length=500)
    public_url: Optional[str] = Field(default=None, max_length=500)
    purpose: Optional[str] = Field(default=None, max_length=100)
    created_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key="t_user.id")
