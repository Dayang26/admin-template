import pytest
from fastapi import HTTPException
from sqlmodel import Session, select

from app.deps.permission import require_permission
from app.models.db import Permission, Role, RolePermission, User, UserRole


def test_require_permission_superuser(session: Session) -> None:
    # Get or create superuser role
    role_superuser = session.exec(select(Role).where(Role.name == "superuser")).first()
    if not role_superuser:
        role_superuser = Role(name="superuser")
        session.add(role_superuser)

    user = User(email="super_perm@example.com", hashed_password="pw")
    session.add(user)
    session.commit()
    session.refresh(role_superuser)
    session.refresh(user)

    session.add(UserRole(user_id=user.id, role_id=role_superuser.id))
    session.commit()

    checker = require_permission("any_resource", "any_action")
    result_user = checker(session=session, current_user=user)

    assert result_user.id == user.id


def test_require_permission_standard_user_success(session: Session) -> None:
    role = Role(name="editor")
    session.add(role)

    user = User(email="editor@example.com", hashed_password="pw")
    session.add(user)

    perm = Permission(resource="article", action="write")
    session.add(perm)
    session.commit()
    session.refresh(role)
    session.refresh(user)
    session.refresh(perm)

    session.add(UserRole(user_id=user.id, role_id=role.id))
    session.add(RolePermission(role_id=role.id, permission_id=perm.id))
    session.commit()

    checker = require_permission("article", "write")
    result_user = checker(session=session, current_user=user)

    assert result_user.id == user.id


def test_require_permission_standard_user_forbidden(session: Session) -> None:
    role = Role(name="viewer")
    session.add(role)

    user = User(email="viewer@example.com", hashed_password="pw")
    session.add(user)

    perm = Permission(resource="article", action="read")
    session.add(perm)
    session.commit()
    session.refresh(role)
    session.refresh(user)
    session.refresh(perm)

    session.add(UserRole(user_id=user.id, role_id=role.id))
    session.add(RolePermission(role_id=role.id, permission_id=perm.id))
    session.commit()

    # Try to access write permission which viewer doesn't have
    checker = require_permission("article", "write")

    with pytest.raises(HTTPException) as exc_info:
        checker(session=session, current_user=user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "权限不足!"
