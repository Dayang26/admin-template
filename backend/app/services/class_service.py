import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.db import Class, UserRole
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
