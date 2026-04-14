from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from app.models.db.base import TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, SQLModel, table=True):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    hashed_password: str
