import logging
from uuid import UUID

from sqlalchemy import create_engine
from sqlmodel import Session, select

from app.core.config import settings
from app.models.db import Permission, Role, RolePermission, User, UserRole
from app.schemas.user import UserCreate
from app.services import user_service

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
logger = logging.getLogger(__name__)

BUILTIN_ROLES: list[dict[str, str]] = [
    {"name": "superuser", "description": "Built-in unrestricted role"},
    {"name": "teacher", "description": "Teacher role with restricted class-scoped operations"},
    {"name": "student", "description": "Student role for self profile access"},
]

BUILTIN_PERMISSIONS: list[dict[str, str]] = [
    {"resource": "class", "action": "create"},
    {"resource": "class", "action": "read"},
    {"resource": "class", "action": "update"},
    {"resource": "class", "action": "delete"},
    {"resource": "user", "action": "create"},
    {"resource": "user", "action": "read"},
    {"resource": "user", "action": "update"},
    {"resource": "user", "action": "delete"},
]

ROLE_PERMISSION_MAP: dict[str, list[tuple[str, str]]] = {
    "superuser": [
        ("class", "create"),
        ("class", "read"),
        ("class", "update"),
        ("class", "delete"),
        ("user", "create"),
        ("user", "read"),
        ("user", "update"),
        ("user", "delete"),
    ],
    "teacher": [
        ("class", "read"),
        ("user", "create"),
        ("user", "read"),
    ],
    "student": [("user", "read")],
}


def _ensure_roles(session: Session) -> dict[str, Role]:
    existing_roles: dict[str, Role] = {role.name: role for role in session.exec(select(Role)).all()}
    for role_def in BUILTIN_ROLES:
        if role_def["name"] not in existing_roles:
            session.add(Role(name=role_def["name"], description=role_def["description"]))
            logger.info("Created role: %s", role_def["name"])
    session.commit()
    return {role.name: role for role in session.exec(select(Role)).all()}


def _ensure_permissions(session: Session) -> dict[tuple[str, str], Permission]:
    existing_permissions: dict[tuple[str, str], Permission] = {(permission.resource, permission.action): permission for permission in session.exec(select(Permission)).all()}
    for perm_def in BUILTIN_PERMISSIONS:
        key = (perm_def["resource"], perm_def["action"])
        if key not in existing_permissions:
            session.add(Permission(resource=perm_def["resource"], action=perm_def["action"]))
            logger.info("Created permission: %s:%s", perm_def["resource"], perm_def["action"])
    session.commit()
    return {(permission.resource, permission.action): permission for permission in session.exec(select(Permission)).all()}


def _ensure_role_permissions(
    session: Session,
    roles: dict[str, Role],
    permissions: dict[tuple[str, str], Permission],
) -> None:
    existing_bindings: set[tuple[UUID, UUID]] = {(binding.role_id, binding.permission_id) for binding in session.exec(select(RolePermission)).all()}
    new_bindings: list[RolePermission] = []

    for role_name, perm_list in ROLE_PERMISSION_MAP.items():
        role = roles.get(role_name)
        if not role:
            logger.warning("Role '%s' not found, skip binding permissions", role_name)
            continue
        for resource, action in perm_list:
            permission = permissions.get((resource, action))
            if not permission:
                logger.warning("Permission '%s:%s' not found, skip binding for role '%s'", resource, action, role_name)
                continue
            if (role.id, permission.id) not in existing_bindings:
                new_bindings.append(RolePermission(role_id=role.id, permission_id=permission.id))

    if new_bindings:
        session.add_all(new_bindings)
        session.commit()
        logger.info("Created %s role-permission bindings", len(new_bindings))


def _ensure_superuser(session: Session, roles: dict[str, Role]) -> None:
    if len(settings.FIRST_SUPERUSER_PASSWORD) < 8:
        raise RuntimeError("FIRST_SUPERUSER_PASSWORD must be at least 8 characters for bootstrap user creation.")

    user = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
    if not user:
        user = user_service.create_user(
            session=session,
            user_create=UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_active=True,
                full_name="superuser",
            ),
        )
        logger.info("Created default superuser user: %s", settings.FIRST_SUPERUSER)

    superuser_role = roles.get("superuser")
    if not superuser_role:
        logger.error("Role 'superuser' not found, cannot bind bootstrap user")
        return

    user_role = session.exec(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == superuser_role.id,
            UserRole.class_id.is_(None),
        )
    ).first()
    if not user_role:
        session.add(UserRole(user_id=user.id, role_id=superuser_role.id, class_id=None))
        session.commit()
        logger.info("Bound user %s to role %s", settings.FIRST_SUPERUSER, superuser_role.name)


def init_db(session: Session) -> None:
    logger.info("Starting database seed initialization")
    roles = _ensure_roles(session)
    permissions = _ensure_permissions(session)
    _ensure_role_permissions(session, roles, permissions)
    _ensure_superuser(session, roles)
    logger.info("Database seed initialization complete")
