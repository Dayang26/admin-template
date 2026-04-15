from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship

from app.models.db.base import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.db.rolePermission import RolePermission
    from app.models.db.userRole import UserRole


class Role(UUIDPrimaryKeyMixin, table=True):
    __tablename__ = "t_role"

    name: str = Field(unique=True, max_length=50)  # superuser / teacher / student
    description: Optional[str] = Field(default=None, max_length=255)

    user_roles: List["UserRole"] = Relationship(back_populates="role")
    role_permissions: List["RolePermission"] = Relationship(back_populates="role")
