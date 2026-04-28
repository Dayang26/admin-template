import uuid

from fastapi import APIRouter, Query
from fastapi.params import Depends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import col, select

from app.deps import AuditInfo, SessionDep
from app.deps.audit import log_audit
from app.deps.auth import get_current_active_superuser
from app.models.db import Class
from app.schemas import ClassMemberAddReq, ClassMemberResp, Response
from app.schemas.user_class import ClassCreateReq, ClassPublicResp, ClassPublicWithCountResp, ClassUpdateReq
from app.services import class_service

router = APIRouter(prefix="/admin/classes", tags=["admin/classes"])


@router.get("/", dependencies=[Depends(get_current_active_superuser)], response_model=Response[Page[ClassPublicWithCountResp]])
def get_classes(
    session: SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    name: str | None = Query(None, description="Search by class name (fuzzy match)"),
) -> Response[Page[ClassPublicWithCountResp]]:
    """分页获取班级列表，包含成员数量。"""
    from sqlmodel import func

    from app.models.db import UserRole

    statement = select(Class)
    if name:
        statement = statement.where(col(Class.name).ilike(f"%{name}%"))
    statement = statement.order_by(col(Class.created_at).desc())

    def _transform_classes(classes: list[Class]) -> list[ClassPublicWithCountResp]:
        result = []
        for c in classes:
            count = session.exec(select(func.count()).select_from(UserRole).where(UserRole.class_id == c.id)).one()
            resp = ClassPublicWithCountResp.model_validate(c)
            resp.member_count = count
            result.append(resp)
        return result

    page_data = paginate(
        session,
        statement,
        params=Params(page=page, size=size),
        transformer=_transform_classes,
    )
    return Response.ok(data=page_data)


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=Response[ClassPublicResp], status_code=201)
def create_class(*, session: SessionDep, class_in: ClassCreateReq, audit: AuditInfo) -> Response[ClassPublicResp]:
    """创建班级。"""
    db_class = class_service.create_class(session=session, class_create=class_in)

    log_audit(session, action="创建班级", detail=f"班级: {class_in.name}", **audit, status_code=201)

    return Response.ok(data=ClassPublicResp.model_validate(db_class), code=201)


@router.get("/{class_id}", dependencies=[Depends(get_current_active_superuser)], response_model=Response[ClassPublicResp])
def get_class(*, session: SessionDep, class_id: uuid.UUID) -> Response[ClassPublicResp]:
    """获取班级详情。"""
    db_class = class_service.get_class(session=session, class_id=class_id)
    return Response.ok(data=ClassPublicResp.model_validate(db_class))


@router.patch("/{class_id}", dependencies=[Depends(get_current_active_superuser)], response_model=Response[ClassPublicResp])
def update_class(*, session: SessionDep, class_id: uuid.UUID, class_in: ClassUpdateReq, audit: AuditInfo) -> Response[ClassPublicResp]:
    """更新班级信息。"""
    db_class = class_service.update_class(session=session, class_id=class_id, class_update=class_in)

    changes = []
    if class_in.name is not None:
        changes.append(f"名称: {class_in.name}")
    if class_in.description is not None:
        changes.append(f"描述: {class_in.description}")
    log_audit(session, action="更新班级", detail=f"班级: {db_class.name}, 变更: {'; '.join(changes)}" if changes else f"班级: {db_class.name}", **audit)

    return Response.ok(data=ClassPublicResp.model_validate(db_class))


@router.delete("/{class_id}", dependencies=[Depends(get_current_active_superuser)], response_model=Response[None])
def delete_class(*, session: SessionDep, class_id: uuid.UUID, audit: AuditInfo) -> Response[None]:
    """删除班级。"""
    db_class = class_service.get_class(session=session, class_id=class_id)
    class_name = db_class.name

    class_service.delete_class(session=session, class_id=class_id)

    log_audit(session, action="删除班级", detail=f"班级: {class_name}", **audit)

    return Response.ok(data=None)


@router.get("/{class_id}/members", dependencies=[Depends(get_current_active_superuser)], response_model=Response[Page[ClassMemberResp]])
def get_class_members(
    *,
    session: SessionDep,
    class_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
) -> Response[Page[ClassMemberResp]]:
    """获取班级成员列表。"""
    from app.models.db import Role, User, UserRole

    class_service.get_class(session=session, class_id=class_id)

    statement = select(UserRole).where(UserRole.class_id == class_id).join(User, User.id == UserRole.user_id).join(Role, Role.id == UserRole.role_id)

    page_data = paginate(
        session,
        statement,
        params=Params(page=page, size=size),
        transformer=lambda items: [
            ClassMemberResp(
                user_id=ur.user_id,
                email=ur.user.email,
                full_name=ur.user.full_name,
                role=ur.role.name,
                joined_at=ur.created_at,
            )
            for ur in items
        ],
    )
    return Response.ok(data=page_data)


@router.post("/{class_id}/members", dependencies=[Depends(get_current_active_superuser)], response_model=Response[None])
def add_class_member(*, session: SessionDep, class_id: uuid.UUID, member_in: ClassMemberAddReq, audit: AuditInfo) -> Response[None]:
    """添加班级成员。"""
    class_service.add_class_member(session=session, class_id=class_id, member_in=member_in)

    log_audit(session, action="添加班级成员", detail=f"班级ID: {class_id}, 用户ID: {member_in.user_id}, 角色: {member_in.role}", **audit)

    return Response.ok(data=None, message="成员已添加")


@router.delete("/{class_id}/members/{user_id}", dependencies=[Depends(get_current_active_superuser)], response_model=Response[None])
def remove_class_member(*, session: SessionDep, class_id: uuid.UUID, user_id: uuid.UUID, audit: AuditInfo) -> Response[None]:
    """移除班级成员。"""
    class_service.remove_class_member(session=session, class_id=class_id, user_id=user_id)

    log_audit(session, action="移除班级成员", detail=f"班级ID: {class_id}, 用户ID: {user_id}", **audit)

    return Response.ok(data=None, message="成员已移除")
