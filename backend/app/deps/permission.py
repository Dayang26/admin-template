from collections.abc import Callable

from fastapi import HTTPException
from sqlmodel import select

from app.deps.auth import CurrentUser
from app.deps.db import SessionDep
from app.models.db import Permission, Role, RolePermission, User, UserRole

SUPERUSER_ROLE_NAME = "superuser"


def require_permission(resource: str, action: str) -> Callable[[SessionDep, CurrentUser], User]:
    def checker(session: SessionDep, current_user: CurrentUser) -> User:
        has_superuser_role = session.exec(select(Role.id).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == current_user.id, Role.name == SUPERUSER_ROLE_NAME)).first()
        if has_superuser_role:
            return current_user

        permission_match = session.exec(
            select(Permission.id)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == current_user.id,
                Permission.resource == resource,
                Permission.action == action,
            )
        ).first()

        if not permission_match:
            raise HTTPException(status_code=403, detail="权限不足!")
        return current_user

    return checker
