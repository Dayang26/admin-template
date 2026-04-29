from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from app.models.db.base import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.db.rolePermission import RolePermission


class Permission(UUIDPrimaryKeyMixin, table=True):
    __tablename__ = "t_permission"
    __table_args__ = (UniqueConstraint("resource", "action", name="uq_permission_resource_action"),)

    resource: str = Field(max_length=50)
    action: str = Field(max_length=50)

    role_permissions: list["RolePermission"] = Relationship(back_populates="permission")
