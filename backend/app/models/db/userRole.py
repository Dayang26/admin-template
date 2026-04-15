from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from app.models.db.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.db.role import Role
    from app.models.db.user import User
    from app.models.db.userClass import Class


class UserRole(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    """class_id 为 NULL 表示全局角色"""

    __tablename__ = "t_user_role"
    __table_args__ = (UniqueConstraint("user_id", "role_id", "class_id", name="uq_user_role_class"),)

    user_id: UUID = Field(foreign_key="t_user.id", index=True)
    role_id: UUID = Field(foreign_key="t_role.id", index=True)
    class_id: UUID | None = Field(default=None, foreign_key="t_class.id", index=True)

    user: Optional["User"] = Relationship(back_populates="user_roles")
    role: Optional["Role"] = Relationship(back_populates="user_roles")
    class_: Optional["Class"] = Relationship(back_populates="user_roles")
