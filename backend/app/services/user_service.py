import logging
import uuid
from typing import TYPE_CHECKING

from fastapi import HTTPException
from fastapi import UploadFile as FastAPIUploadFile
from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.db import Role, UploadFile, User, UserRole
from app.schemas.upload import UploadFileType, UploadVisibility
from app.schemas.user import (
    UserCreateByAdminReq,
    UserCreateReq,
    UserDetailResp,
    UserPublicResp,
    UserResetPasswordReq,
    UserUpdateMeReq,
    UserUpdatePasswordReq,
    UserUpdateReq,
)
from app.services import upload_service

if TYPE_CHECKING:
    from app.deps.audit import AuditInfo

logger = logging.getLogger(__name__)
USER_AVATAR_UPLOAD_PURPOSE = "user_avatar"


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def create_user(*, session: Session, user_create: UserCreateReq) -> User:
    db_obj = User.model_validate(
        user_create,
        update={"hashed_password": get_password_hash(user_create.password)},
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def build_user_public_resp(user: User) -> UserPublicResp:
    avatar_file = user.avatar_file
    avatar_url = avatar_file.public_url if avatar_file else None
    return UserPublicResp(
        **user.model_dump(),
        avatar_url=avatar_url,
    )


def get_roles_by_names(*, session: Session, role_names: list[str]) -> list[Role]:
    statement = select(Role).where(Role.name.in_(role_names))
    return list(session.exec(statement).all())


def create_user_with_roles(*, session: Session, user_create: UserCreateByAdminReq) -> User:
    unique_roles = list(dict.fromkeys(user_create.roles))

    if get_user_by_email(session=session, email=user_create.email):
        raise HTTPException(status_code=400, detail="A user with this email already exists")

    roles = get_roles_by_names(session=session, role_names=unique_roles)
    missing = set(unique_roles) - {r.name for r in roles}
    if missing:
        raise HTTPException(status_code=400, detail=f"Role(s) not found: {', '.join(sorted(missing))}")

    if "superuser" in unique_roles:
        raise HTTPException(status_code=400, detail="Cannot assign the 'superuser' role")

    db_obj = User.model_validate(
        user_create,
        update={"hashed_password": get_password_hash(user_create.password)},
    )
    session.add(db_obj)
    session.flush()

    for role in roles:
        session.add(UserRole(user_id=db_obj.id, role_id=role.id))

    session.commit()
    session.refresh(db_obj)
    return db_obj


# Superuser role name used in the system (note: differs from SUPERADMIN in permission.py)
SUPERUSER_ROLE_NAME = "superuser"


def _get_user_role_names(*, session: Session, user_id: uuid.UUID) -> set[str]:
    statement = select(Role.name).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user_id)
    return set(session.exec(statement).all())


def _ensure_can_modify_target_user(*, session: Session, target_user_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
    target_roles = _get_user_role_names(session=session, user_id=target_user_id)

    if SUPERUSER_ROLE_NAME in target_roles and target_user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot modify information of other superusers",
        )


def update_user_by_admin(
    *,
    session: Session,
    user_update: UserUpdateReq,
    target_user_id: uuid.UUID,
    current_user_id: uuid.UUID,
) -> User:
    """Update a user by admin (superuser).

    Performs the following:
    1. Check if target user exists
    2. Check superuser mutual exclusion (cannot modify other superusers)
    3. Update basic fields (full_name, is_active)
    4. Update password if provided
    5. Replace roles if provided (clear old roles, bind new roles)
    """
    # 1. Check if target user exists
    target_user = session.get(User, target_user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Check superuser mutual exclusion
    _ensure_can_modify_target_user(session=session, target_user_id=target_user_id, current_user_id=current_user_id)

    # 3. Update basic fields
    update_data = user_update.model_dump(exclude_unset=True, exclude={"password", "roles"})
    for field, value in update_data.items():
        if value is not None:
            setattr(target_user, field, value)

    # 4. Update password if provided
    if user_update.password:
        target_user.hashed_password = get_password_hash(user_update.password)

    # 5. Replace roles if provided
    if user_update.roles is not None:
        unique_roles = list(dict.fromkeys(user_update.roles))

        # Check if trying to assign superuser role
        if SUPERUSER_ROLE_NAME in unique_roles:
            raise HTTPException(status_code=400, detail="Cannot assign the 'superuser' role")

        # Find roles in database
        roles = get_roles_by_names(session=session, role_names=unique_roles)
        missing = set(unique_roles) - {r.name for r in roles}
        if missing:
            raise HTTPException(status_code=400, detail=f"Role(s) not found: {', '.join(sorted(missing))}")

        # Replace role associations without deleting/re-inserting unchanged rows.
        statement = select(UserRole).where(UserRole.user_id == target_user_id)
        existing_user_roles = session.exec(statement).all()
        desired_role_ids = {role.id for role in roles}
        existing_role_ids = {user_role.role_id for user_role in existing_user_roles}

        for existing_user_role in existing_user_roles:
            if existing_user_role.role_id not in desired_role_ids:
                session.delete(existing_user_role)

        for role in roles:
            if role.id not in existing_role_ids:
                session.add(UserRole(user_id=target_user_id, role_id=role.id))

    session.add(target_user)
    session.commit()
    session.refresh(target_user)
    return target_user


def reset_user_password_by_admin(
    *,
    session: Session,
    password_in: UserResetPasswordReq,
    target_user_id: uuid.UUID,
    current_user_id: uuid.UUID,
) -> User:
    target_user = session.get(User, target_user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    _ensure_can_modify_target_user(session=session, target_user_id=target_user_id, current_user_id=current_user_id)

    target_user.hashed_password = get_password_hash(password_in.new_password)
    session.add(target_user)
    session.commit()
    session.refresh(target_user)
    return target_user


def update_user_me(*, session: Session, user_update: UserUpdateMeReq, current_user: User) -> User:
    """Update current user's own profile. Only allows updating full_name."""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name

    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


def replace_user_avatar(
    *,
    session: Session,
    current_user: User,
    file: FastAPIUploadFile,
    audit_info: "AuditInfo",
) -> User:
    previous_avatar_file_id = current_user.avatar_file_id
    uploaded_avatar = upload_service.process_upload(
        session=session,
        file=file,
        file_type=UploadFileType.image.value,
        visibility=UploadVisibility.public.value,
        purpose=USER_AVATAR_UPLOAD_PURPOSE,
        created_by_id=current_user.id,
        audit_info=audit_info,
        log_upload_audit=False,
    )

    try:
        current_user.avatar_file_id = uploaded_avatar.id
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
    except Exception:
        session.rollback()
        _cleanup_avatar_upload(session=session, upload_file_id=uploaded_avatar.id, owner_id=current_user.id)
        raise

    if previous_avatar_file_id and previous_avatar_file_id != uploaded_avatar.id:
        _cleanup_avatar_upload(session=session, upload_file_id=previous_avatar_file_id, owner_id=current_user.id)

    return current_user


def remove_user_avatar(*, session: Session, current_user: User) -> User:
    previous_avatar_file_id = current_user.avatar_file_id
    if previous_avatar_file_id is None:
        return current_user

    current_user.avatar_file_id = None
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    _cleanup_avatar_upload(
        session=session,
        upload_file_id=previous_avatar_file_id,
        owner_id=current_user.id,
    )

    return current_user


def get_user_detail(*, session: Session, user_id: uuid.UUID) -> UserDetailResp:
    """Get user details including roles and permissions."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    roles = []

    for user_role in user.user_roles:
        if user_role.role:
            roles.append(user_role.role.name)

    # 收集用户所有权限（通过角色的权限绑定）
    permissions_set: set[str] = set()
    for role_name in roles:
        role = session.exec(select(Role).where(Role.name == role_name)).first()
        if role:
            for rp in role.role_permissions:
                if rp.permission:
                    permissions_set.add(f"{rp.permission.resource}:{rp.permission.action}")

    return UserDetailResp(
        **build_user_public_resp(user).model_dump(),
        roles=roles,
        permissions=sorted(permissions_set),
    )


def delete_user(*, session: Session, target_user_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
    """Delete a user, cleaning up role associations first."""
    target_user = session.get(User, target_user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 禁止删除自己
    if target_user_id == current_user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    # 禁止删除其他超级管理员
    statement = select(Role.name).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == target_user_id)
    target_roles = set(session.exec(statement).all())

    if SUPERUSER_ROLE_NAME in target_roles:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete other superusers",
        )

    avatar_file_id = target_user.avatar_file_id
    if avatar_file_id is not None:
        target_user.avatar_file_id = None
        session.add(target_user)
        session.flush()
        _cleanup_avatar_upload(session=session, upload_file_id=avatar_file_id, owner_id=target_user_id)

    # 删除角色关联
    statement = select(UserRole).where(UserRole.user_id == target_user_id)
    user_roles = session.exec(statement).all()
    for ur in user_roles:
        session.delete(ur)

    session.delete(target_user)
    session.commit()


def update_user_password(*, session: Session, password_in: UserUpdatePasswordReq, current_user: User) -> None:
    """Update current user's password after verifying the current one."""
    # 验证旧密码
    is_correct, _ = verify_password(password_in.current_password, current_user.hashed_password)
    if not is_correct:
        raise HTTPException(status_code=400, detail="Incorrect current password")

    # 哈希新密码并保存
    current_user.hashed_password = get_password_hash(password_in.new_password)
    session.add(current_user)
    session.commit()


def _cleanup_avatar_upload(*, session: Session, upload_file_id: uuid.UUID, owner_id: uuid.UUID) -> None:
    upload_file = session.get(UploadFile, upload_file_id)
    if not upload_file:
        return
    if upload_file.purpose != USER_AVATAR_UPLOAD_PURPOSE:
        return
    if upload_file.created_by_id != owner_id:
        return

    try:
        upload_service.delete_upload_file(session=session, upload_file=upload_file)
    except Exception:
        session.rollback()
        logger.exception("Failed to cleanup avatar upload: %s", upload_file_id)
