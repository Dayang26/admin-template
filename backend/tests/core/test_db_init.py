from sqlmodel import select

from app.core.config import settings
from app.core.db import BUILTIN_PERMISSIONS, BUILTIN_ROLES, ROLE_PERMISSION_MAP, init_db
from app.models.db import Permission, Role, RolePermission, User, UserRole


def test_init_db_seeds_roles_permissions_and_superuser(session) -> None:
    init_db(session)

    roles = session.exec(select(Role)).all()
    role_map = {role.name: role for role in roles}
    assert {role_def["name"] for role_def in BUILTIN_ROLES}.issubset(set(role_map))

    permissions = session.exec(select(Permission)).all()
    permission_map = {(permission.resource, permission.action): permission for permission in permissions}
    assert {(perm["resource"], perm["action"]) for perm in BUILTIN_PERMISSIONS}.issubset(set(permission_map))

    role_permissions = session.exec(select(RolePermission)).all()
    role_permission_pairs = {(rp.role_id, rp.permission_id) for rp in role_permissions}

    for role_name, perm_list in ROLE_PERMISSION_MAP.items():
        role = role_map[role_name]
        for resource, action in perm_list:
            permission = permission_map[(resource, action)]
            assert (role.id, permission.id) in role_permission_pairs

    superuser = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
    assert superuser is not None
    superuser_role = role_map["superuser"]
    superuser_binding = session.exec(
        select(UserRole).where(
            UserRole.user_id == superuser.id,
            UserRole.role_id == superuser_role.id,
        )
    ).first()
    assert superuser_binding is not None


def test_init_db_is_idempotent(session) -> None:
    init_db(session)
    counts_before = {
        "role": len(session.exec(select(Role)).all()),
        "permission": len(session.exec(select(Permission)).all()),
        "role_permission": len(session.exec(select(RolePermission)).all()),
        "superuser_bindings": len(session.exec(select(UserRole).join(Role, Role.id == UserRole.role_id).where(Role.name == "superuser")).all()),
    }

    init_db(session)
    counts_after = {
        "role": len(session.exec(select(Role)).all()),
        "permission": len(session.exec(select(Permission)).all()),
        "role_permission": len(session.exec(select(RolePermission)).all()),
        "superuser_bindings": len(session.exec(select(UserRole).join(Role, Role.id == UserRole.role_id).where(Role.name == "superuser")).all()),
    }

    assert counts_after == counts_before
