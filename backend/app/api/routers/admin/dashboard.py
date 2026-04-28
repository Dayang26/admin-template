from fastapi import APIRouter, Depends
from sqlmodel import func, select

from app.deps import SessionDep
from app.deps.auth import get_current_active_superuser
from app.models.db import Class, Role, User, UserRole
from app.schemas import Response

router = APIRouter(prefix="/admin/dashboard", tags=["admin/dashboard"])


@router.get("/stats", dependencies=[Depends(get_current_active_superuser)], response_model=Response[dict])
def get_dashboard_stats(session: SessionDep) -> Response[dict]:
    """获取系统概览统计数据。"""
    total_users = session.exec(select(func.count()).select_from(User)).one()
    active_users = session.exec(
        select(func.count()).select_from(User).where(User.is_active == True)  # noqa: E712
    ).one()
    total_classes = session.exec(select(func.count()).select_from(Class)).one()

    # 角色分布：统计每个全局角色（class_id IS NULL）的用户数
    role_rows = session.exec(
        select(Role.name, func.count(UserRole.id))
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.class_id == None)  # noqa: E711
        .group_by(Role.name)
    ).all()
    role_distribution = dict(role_rows)

    return Response.ok(
        data={
            "total_users": total_users,
            "active_users": active_users,
            "total_classes": total_classes,
            "role_distribution": role_distribution,
        }
    )
