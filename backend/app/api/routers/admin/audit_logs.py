from datetime import datetime

from fastapi import APIRouter, Query
from fastapi.params import Depends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import col, select

from app.deps import SessionDep
from app.deps.permission import require_permission
from app.models.db.audit_log import AuditLog
from app.schemas import Response

router = APIRouter(prefix="/admin/audit-logs", tags=["admin/audit-logs"])


@router.get("/", dependencies=[Depends(require_permission("audit_log", "read"))], response_model=Response[Page[dict]])
def get_audit_logs(
    session: SessionDep,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_email: str | None = Query(None, description="按用户邮箱筛选（模糊）"),
    action: str | None = Query(None, description="按操作类型筛选（精确）"),
    start_date: datetime | None = Query(None, description="开始时间"),
    end_date: datetime | None = Query(None, description="结束时间"),
) -> Response[Page[dict]]:
    """获取操作日志列表，支持分页和筛选。"""
    statement = select(AuditLog).order_by(col(AuditLog.created_at).desc())

    if user_email:
        statement = statement.where(col(AuditLog.user_email).ilike(f"%{user_email}%"))
    if action:
        statement = statement.where(AuditLog.action == action)
    if start_date:
        statement = statement.where(AuditLog.created_at >= start_date)
    if end_date:
        statement = statement.where(AuditLog.created_at <= end_date)

    page_data = paginate(
        session,
        statement,
        params=Params(page=page, size=size),
        transformer=lambda logs: [
            {
                "id": str(log.id),
                "created_at": log.created_at.isoformat(),
                "user_id": str(log.user_id) if log.user_id else None,
                "user_email": log.user_email,
                "method": log.method,
                "path": log.path,
                "action": log.action,
                "detail": log.detail,
                "status_code": log.status_code,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
            }
            for log in logs
        ],
    )
    return Response.ok(data=page_data)
