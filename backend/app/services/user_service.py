import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models.db import Role, User, UserRole
from app.schemas.user import (
    UserCreateByAdminReq,
    UserCreateReq,
    UserUpdateMeReq,
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

        # Delete old role associations
        statement = select(UserRole).where(UserRole.user_id == target_user_id)
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
