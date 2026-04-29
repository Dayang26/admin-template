from fastapi import APIRouter, Depends
from sqlmodel import func, select

from app.deps import SessionDep
from app.deps.permission import require_permission
from app.models.db import Role, User, UserRole
from app.schemas import Response

router = APIRouter(prefix="/admin/dashboard", tags=["admin/dashboard"])


@router.get("/stats", dependencies=[Depends(require_permission("dashboard", "read"))], response_model=Response[dict])
def get_dashboard_stats(session: SessionDep) -> Response[dict]:
    """获取系统概览统计数据。"""
    total_users = session.exec(select(func.count()).select_from(User)).one()
    active_users = session.exec(
        select(func.count()).select_from(User).where(User.is_active == True)  # noqa: E712
    ).one()

    # 角色分布：统计每个角色的用户数
    role_rows = session.exec(select(Role.name, func.count(UserRole.id)).join(UserRole, UserRole.role_id == Role.id).group_by(Role.name)).all()
    role_distribution = dict(role_rows)

    return Response.ok(
        data={
            "total_users": total_users,
            "active_users": active_users,
            "role_distribution": role_distribution,
        }
    )
