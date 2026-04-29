from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from app.models.db.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.db.role import Role
    from app.models.db.user import User


class UserRole(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    """User-to-role binding."""

    __tablename__ = "t_user_role"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    user_id: UUID = Field(foreign_key="t_user.id", index=True)
    role_id: UUID = Field(foreign_key="t_role.id", index=True)

    user: Optional["User"] = Relationship(back_populates="user_roles")
    role: Optional["Role"] = Relationship(back_populates="user_roles")
