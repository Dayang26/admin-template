import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.db import Class, Role, User, UserRole
from app.schemas.class_member import ClassMemberAddReq
from app.schemas.user_class import ClassCreateReq, ClassUpdateReq


def create_class(*, session: Session, class_create: ClassCreateReq) -> Class:
    statement = select(Class).where(Class.name == class_create.name)
    if session.exec(statement).first():
        raise HTTPException(status_code=400, detail="The class name already exists in the system.")
    db_class = Class.model_validate(class_create)
    session.add(db_class)
    session.commit()
    session.refresh(db_class)
    return db_class


def update_class(*, session: Session, class_id: uuid.UUID, class_update: ClassUpdateReq) -> Class:
    db_class = session.get(Class, class_id)
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found.")

    if class_update.name is not None and class_update.name != db_class.name:
        statement = select(Class).where(Class.name == class_update.name)
        if session.exec(statement).first():
            raise HTTPException(status_code=400, detail="The class name already exists in the system.")

    update_data = class_update.model_dump(exclude_unset=True)
    db_class.sqlmodel_update(update_data)
    session.add(db_class)
    session.commit()
    session.refresh(db_class)
    return db_class


def delete_class(*, session: Session, class_id: uuid.UUID) -> None:
    db_class = session.get(Class, class_id)
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found.")

    statement = select(UserRole).where(UserRole.class_id == class_id)
    if session.exec(statement).first():
        raise HTTPException(status_code=400, detail="该班级下存在关联用户角色，无法删除")

    session.delete(db_class)
    session.commit()


def get_class(*, session: Session, class_id: uuid.UUID) -> Class:
    db_class = session.get(Class, class_id)
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found.")
    return db_class


def add_class_member(*, session: Session, class_id: uuid.UUID, member_in: ClassMemberAddReq) -> UserRole:
    """Assign a user to a class with a specific role."""
    # 检查班级是否存在
    db_class = session.get(Class, class_id)
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")

    # 检查用户是否存在
    db_user = session.get(User, member_in.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 检查角色是否存在
    statement = select(Role).where(Role.name == member_in.role)
    db_role = session.exec(statement).first()
    if not db_role:
        raise HTTPException(status_code=400, detail=f"Role '{member_in.role}' not found")

    # 检查是否已存在完全相同的关联
    statement = select(UserRole).where(
        UserRole.user_id == member_in.user_id,
        UserRole.role_id == db_role.id,
        UserRole.class_id == class_id,
    )
    if session.exec(statement).first():
        raise HTTPException(status_code=400, detail="User already has this role in the class")

    db_user_role = UserRole(user_id=member_in.user_id, role_id=db_role.id, class_id=class_id)
    session.add(db_user_role)
    session.commit()
    session.refresh(db_user_role)
    return db_user_role


def remove_class_member(*, session: Session, class_id: uuid.UUID, user_id: uuid.UUID) -> None:
    """Remove a user from a class by deleting all their role associations within that class."""
    statement = select(UserRole).where(UserRole.user_id == user_id, UserRole.class_id == class_id)
    user_roles = session.exec(statement).all()
    if not user_roles:
        raise HTTPException(status_code=404, detail="Member not found in this class")

    for ur in user_roles:
        session.delete(ur)
    session.commit()
