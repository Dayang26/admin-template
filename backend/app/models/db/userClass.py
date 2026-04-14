from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship

from app.models.db.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.db.userRole import UserRole


class Class(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "t_class"

    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)

    user_roles: List["UserRole"] = Relationship(back_populates="class_")
