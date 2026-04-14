from typing import TYPE_CHECKING, List

from app.models.db.base import TimestampMixin, UUIDPrimaryKeyMixin
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.db.userRole import UserRole


class User(UUIDPrimaryKeyMixin, TimestampMixin, SQLModel, table=True):
    __tablename__ = "t_user"

    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    full_name: str | None = Field(default=None, max_length=255)
    hashed_password: str
    user_roles: List["UserRole"] = Relationship(back_populates="user")
