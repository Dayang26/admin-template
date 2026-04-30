import logging
from uuid import UUID

from sqlalchemy import create_engine, tuple_
from sqlmodel import Session, select

from app.core.config import settings
from app.models.db import Permission, Role, RolePermission, User, UserRole
from app.schemas.user import UserCreateReq
from app.services import user_service

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
logger = logging.getLogger(__name__)

BUILTIN_ROLES: list[dict[str, str]] = [
    {"name": "superuser", "description": "Built-in unrestricted role"},
]

BUILTIN_PERMISSIONS: list[dict[str, str]] = [
    {"resource": "user", "action": "create"},
    {"resource": "user", "action": "read"},
    {"resource": "user", "action": "update"},
    {"resource": "user", "action": "delete"},
    {"resource": "role", "action": "create"},
    {"resource": "role", "action": "read"},
    {"resource": "role", "action": "update"},
    {"resource": "role", "action": "delete"},
    {"resource": "audit_log", "action": "read"},
    {"resource": "dashboard", "action": "read"},
    {"resource": "system_setting", "action": "read"},
    {"resource": "system_setting", "action": "update_system_name"},
    {"resource": "system_setting", "action": "update_tagline"},
    {"resource": "system_setting", "action": "update_copyright"},
    {"resource": "system_setting", "action": "update_page_title_template"},
    {"resource": "system_setting", "action": "upload_logo"},
    {"resource": "system_setting", "action": "upload_favicon"},
    {"resource": "system_setting", "action": "upload_login_background"},
]

ROLE_PERMISSION_MAP: dict[str, list[tuple[str, str]]] = {
    "superuser": [
        ("user", "create"),
        ("user", "read"),
        ("user", "update"),
        ("user", "delete"),
        ("role", "create"),
        ("role", "read"),
        ("role", "update"),
        ("role", "delete"),
        ("audit_log", "read"),
        ("dashboard", "read"),
        ("system_setting", "read"),
        ("system_setting", "update_system_name"),
        ("system_setting", "update_tagline"),
        ("system_setting", "update_copyright"),
        ("system_setting", "update_page_title_template"),
        ("system_setting", "upload_logo"),
        ("system_setting", "upload_favicon"),
        ("system_setting", "upload_login_background"),
    ],
}

OBSOLETE_PERMISSIONS: set[tuple[str, str]] = {
    ("upload", "create"),
    ("system_setting", "update"),
    ("system_setting_logo", "upload"),
    ("system_setting_favicon", "upload"),
    ("system_setting_login_background", "upload"),
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
    obsolete_permissions = session.exec(
        select(Permission).where(
            tuple_(Permission.resource, Permission.action).in_(OBSOLETE_PERMISSIONS),
        )
    ).all()
    if obsolete_permissions:
        obsolete_permission_ids = [permission.id for permission in obsolete_permissions]
        obsolete_bindings = session.exec(select(RolePermission).where(RolePermission.permission_id.in_(obsolete_permission_ids))).all()
        for binding in obsolete_bindings:
            session.delete(binding)
        for permission in obsolete_permissions:
            session.delete(permission)
        session.commit()

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
            user_create=UserCreateReq(
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
        )
    ).first()
    if not user_role:
        session.add(UserRole(user_id=user.id, role_id=superuser_role.id))
        session.commit()
        logger.info("Bound user %s to role %s", settings.FIRST_SUPERUSER, superuser_role.name)


def _ensure_system_settings(session: Session) -> None:
    from app.models.db.system_setting import SystemSetting

    setting = session.exec(select(SystemSetting).where(SystemSetting.setting_key == "default")).first()
    if not setting:
        setting = SystemSetting(
            setting_key="default",
            system_name="Carrier Agent",
            tagline="管理后台",
            page_title_template="{page} - {systemName}",
        )
        session.add(setting)
        session.commit()
        logger.info("Created default system settings")


def init_db(session: Session) -> None:
    logger.info("Starting database seed initialization")
    roles = _ensure_roles(session)
    permissions = _ensure_permissions(session)
    _ensure_role_permissions(session, roles, permissions)
    _ensure_superuser(session, roles)
    _ensure_system_settings(session)
    logger.info("Database seed initialization complete")
