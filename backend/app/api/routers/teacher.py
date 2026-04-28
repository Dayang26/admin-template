import uuid

from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import select

from app.deps import SessionDep
from app.deps.auth import CurrentUser
from app.deps.permission import require_permission
from app.models.db import Role, User, UserRole
from app.schemas import ClassMemberResp, ClassPublicResp, Response
from app.services import user_service

router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.get("/classes", dependencies=[Depends(require_permission("class", "read"))], response_model=Response[list[ClassPublicResp]])
def get_my_classes(
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response[list[ClassPublicResp]]:
    """Get classes where the current user (teacher) is a member."""
    classes = user_service.get_teacher_classes(session=session, teacher_id=current_user.id)
    return Response.ok(data=[ClassPublicResp.model_validate(c) for c in classes])


@router.get("/classes/{class_id}/members", dependencies=[Depends(require_permission("class", "read"))], response_model=Response[Page[ClassMemberResp]])
def get_class_members(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    class_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
) -> Response[Page[ClassMemberResp]]:
    """Get members of a class, provided the current user is a member of that class."""
    # 权限检查：当前用户必须是该班级的成员
    statement = select(UserRole).where(UserRole.user_id == current_user.id, UserRole.class_id == class_id)
    if not session.exec(statement).first():
        raise HTTPException(status_code=403, detail="You are not a member of this class")

    # 查询成员列表
    query = select(UserRole).where(UserRole.class_id == class_id).join(User, User.id == UserRole.user_id).join(Role, Role.id == UserRole.role_id)

    page_data = paginate(
        session,
        query,
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
