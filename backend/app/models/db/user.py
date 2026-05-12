import uuid
from typing import TYPE_CHECKING, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.models.db.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.db.upload_file import UploadFile
    from app.models.db.userRole import UserRole


class User(UUIDPrimaryKeyMixin, TimestampMixin, SQLModel, table=True):
    __tablename__ = "t_user"

    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    full_name: str | None = Field(default=None, max_length=255)
    avatar_file_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="t_upload_file.id",
        ondelete="SET NULL",
        nullable=True,
    )
    hashed_password: str
    avatar_file: Optional["UploadFile"] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "foreign_keys": "User.avatar_file_id",
        },
    )
    user_roles: list["UserRole"] = Relationship(back_populates="user")
