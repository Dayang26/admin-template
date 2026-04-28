import uuid

from fastapi import APIRouter, Query
from fastapi.params import Depends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import col, select

from app.deps import AuditInfo, SessionDep
from app.deps.audit import log_audit
from app.deps.auth import CurrentUser
from app.deps.permission import require_permission
from app.models.db import User
from app.schemas import (
    Response,
    UserCreateByAdminReq,
    UserDetailResp,
    UserPublicResp,
    UserUpdateReq,
)
from app.schemas.user import UserPublicWithRolesResp
from app.services import user_service

router = APIRouter(prefix="/admin/users", tags=["admin"])


@router.get("/", dependencies=[Depends(require_permission("user", "read"))], response_model=Response[Page[UserPublicWithRolesResp]])
def get_users(
    session: SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    q: str | None = Query(None, description="Search by email or full name (fuzzy, OR logic)"),
    email: str | None = Query(None, description="Filter by email (fuzzy)"),
    full_name: str | None = Query(None, description="Filter by full name (fuzzy)"),
    role: str | None = Query(None, description="Filter by role name"),
    class_id: uuid.UUID | None = Query(None, description="Filter by class ID"),
) -> Response[Page[UserPublicWithRolesResp]]:
    """分页获取用户列表，支持多种筛选条件。"""
    from app.models.db import Role, UserRole

    statement = select(User).order_by(col(User.created_at).desc())

    if q:
        statement = statement.where(col(User.email).ilike(f"%{q}%") | col(User.full_name).ilike(f"%{q}%"))

    if email:
        statement = statement.where(col(User.email).ilike(f"%{email}%"))
    if full_name:
        statement = statement.where(col(User.full_name).ilike(f"%{full_name}%"))

    if role or class_id:
        statement = statement.join(UserRole, UserRole.user_id == User.id)
        if role:
            statement = statement.join(Role, UserRole.role_id == Role.id).where(Role.name == role)
        if class_id:
            statement = statement.where(UserRole.class_id == class_id)
        statement = statement.distinct()

    def _transform_users(users: list[User]) -> list[UserPublicWithRolesResp]:
        result = []
        for user in users:
            # 查询该用户的全局角色
            role_names = [
                ur.role.name
                for ur in session.exec(
                    select(UserRole).where(UserRole.user_id == user.id, UserRole.class_id == None)  # noqa: E711
                ).all()
                if ur.role
            ]
            resp = UserPublicWithRolesResp.model_validate(user)
            resp.roles = role_names
            result.append(resp)
        return result

    page_data = paginate(
        session,
        statement,
        params=Params(page=page, size=size),
        transformer=_transform_users,
    )
    return Response.ok(data=page_data)


@router.post("/", dependencies=[Depends(require_permission("user", "create"))], response_model=Response[UserPublicResp], status_code=201)
def create_user_by_admin(*, session: SessionDep, user_in: UserCreateByAdminReq, audit: AuditInfo) -> Response[UserPublicResp]:
    """管理员创建用户并分配角色。"""
    user = user_service.create_user_with_roles(session=session, user_create=user_in)

    log_audit(
        session,
        action="创建用户",
        detail=f"邮箱: {user_in.email}, 角色: {', '.join(user_in.roles)}",
        **audit,
        status_code=201,
    )

    return Response.ok(data=UserPublicResp.model_validate(user), code=201)


@router.patch("/{user_id}", dependencies=[Depends(require_permission("user", "update"))], response_model=Response[UserPublicResp])
def update_user_by_admin(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdateReq,
    current_user: CurrentUser,
    audit: AuditInfo,
) -> Response[UserPublicResp]:
    """管理员更新用户信息。"""
    user = user_service.update_user_by_admin(
        session=session,
        user_update=user_in,
        target_user_id=user_id,
        current_user_id=current_user.id,
    )

    changes = []
    if user_in.full_name is not None:
        changes.append(f"姓名: {user_in.full_name}")
    if user_in.password is not None:
        changes.append("密码已修改")
    if user_in.is_active is not None:
        changes.append(f"状态: {'活跃' if user_in.is_active else '禁用'}")
    if user_in.roles is not None:
        changes.append(f"角色: {', '.join(user_in.roles)}")

    log_audit(
        session,
        action="更新用户",
        detail=f"用户: {user.email}, 变更: {'; '.join(changes)}" if changes else f"用户: {user.email}",
        **audit,
    )

    return Response.ok(data=UserPublicResp.model_validate(user))


@router.get("/{user_id}", dependencies=[Depends(require_permission("user", "read"))], response_model=Response[UserDetailResp])
def get_user_detail(*, session: SessionDep, user_id: uuid.UUID) -> Response[UserDetailResp]:
    """获取指定用户详情。"""
    user_detail = user_service.get_user_detail(session=session, user_id=user_id)
    return Response.ok(data=user_detail)


@router.delete("/{user_id}", dependencies=[Depends(require_permission("user", "delete"))], response_model=Response[None])
def delete_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: CurrentUser,
    audit: AuditInfo,
) -> Response[None]:
    """删除用户。"""
    # 先获取用户邮箱用于日志
    target_user = session.get(User, user_id)
    target_email = target_user.email if target_user else str(user_id)

    user_service.delete_user(
        session=session,
        target_user_id=user_id,
        current_user_id=current_user.id,
    )

    log_audit(session, action="删除用户", detail=f"用户: {target_email}", **audit)

    return Response.ok(data=None, message="用户已删除")
