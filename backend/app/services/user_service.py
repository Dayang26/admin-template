import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.db import Class, Role, User, UserRole
from app.schemas.user import (
    ClassMembershipResp,
    UserCreateByAdminReq,
    UserCreateReq,
    UserDetailResp,
    UserUpdateMeReq,
    UserUpdatePasswordReq,
    UserUpdateReq,
)


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
        session.add(UserRole(user_id=db_obj.id, role_id=role.id, class_id=None))

    session.commit()
    session.refresh(db_obj)
    return db_obj


# Superuser role name used in the system (note: differs from SUPERADMIN in permission.py)
SUPERUSER_ROLE_NAME = "superuser"


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
    # Query target user's current roles
    statement = select(Role.name).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == target_user_id)
    target_roles = set(session.exec(statement).all())

    if SUPERUSER_ROLE_NAME in target_roles and target_user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot modify information of other superusers",
        )

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

        # Delete old GLOBAL role associations (preserve class-level roles)
        statement = select(UserRole).where(
            UserRole.user_id == target_user_id,
            UserRole.class_id == None,  # noqa: E711
        )
        old_user_roles = session.exec(statement).all()
        for old_user_role in old_user_roles:
            session.delete(old_user_role)

        # Create new role associations
        for role in roles:
            session.add(UserRole(user_id=target_user_id, role_id=role.id, class_id=None))

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


def get_user_detail(*, session: Session, user_id: uuid.UUID) -> UserDetailResp:
    """Get user details including global roles, permissions and class memberships."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    global_roles = []
    class_memberships = []

    for user_role in user.user_roles:
        if user_role.class_id is None:
            if user_role.role:
                global_roles.append(user_role.role.name)
        else:
            if user_role.role and user_role.class_:
                class_memberships.append(
                    ClassMembershipResp(
                        class_id=user_role.class_id,
                        class_name=user_role.class_.name,
                        role=user_role.role.name,
                    )
                )

    # 收集用户所有权限（通过全局角色的权限绑定）
    permissions_set: set[str] = set()
    for role_name in global_roles:
        role = session.exec(select(Role).where(Role.name == role_name)).first()
        if role:
            for rp in role.role_permissions:
                if rp.permission:
                    permissions_set.add(f"{rp.permission.resource}:{rp.permission.action}")

    return UserDetailResp(
        **user.model_dump(),
        roles=global_roles,
        permissions=sorted(permissions_set),
        class_memberships=class_memberships,
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


def get_teacher_classes(*, session: Session, teacher_id: uuid.UUID) -> list[Class]:
    """Get all classes where the user has any role assigned."""
    statement = select(Class).join(UserRole, UserRole.class_id == Class.id).where(UserRole.user_id == teacher_id).order_by(Class.name)
    return list(session.exec(statement).all())
