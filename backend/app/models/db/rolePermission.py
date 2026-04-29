from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from app.models.db.base import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.db.permission import Permission
    from app.models.db.role import Role


class RolePermission(UUIDPrimaryKeyMixin, table=True):
    __tablename__ = "t_role_permission"
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)

    role_id: UUID = Field(foreign_key="t_role.id", index=True)
    permission_id: UUID = Field(foreign_key="t_permission.id", index=True)

    role: Optional["Role"] = Relationship(back_populates="role_permissions")
    permission: Optional["Permission"] = Relationship(back_populates="role_permissions")
