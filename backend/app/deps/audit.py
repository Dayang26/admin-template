import logging
import uuid
from typing import Annotated

from fastapi import Depends, Request
from sqlmodel import Session

from app.deps.auth import CurrentUser
from app.models.db.audit_log import AuditLog

logger = logging.getLogger(__name__)


def _get_client_ip(request: Request) -> str | None:
    """获取客户端真实 IP，支持反向代理。"""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def get_audit_info(request: Request, current_user: CurrentUser) -> dict:
    """提取审计所需的请求上下文信息，通过依赖注入提供给路由函数。"""
    return {
        "user_id": current_user.id,
        "user_email": current_user.email,
        "method": request.method,
        "path": str(request.url.path),
        "ip_address": _get_client_ip(request),
        "user_agent": request.headers.get("user-agent", "")[:500],
    }


AuditInfo = Annotated[dict, Depends(get_audit_info)]


def log_audit(
    session: Session,
    *,
    action: str,
    user_id: uuid.UUID,
    user_email: str,
    method: str,
    path: str,
    detail: str | None = None,
    status_code: int = 200,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    """写入一条审计日志记录。在路由函数操作成功后调用。"""
    try:
        log_entry = AuditLog(
            user_id=user_id,
            user_email=user_email,
            method=method,
            path=path,
            action=action,
            detail=detail,
            status_code=status_code,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        session.add(log_entry)
        session.commit()
        logger.info("审计日志已记录: action=%s, user=%s", action, user_email)
    except Exception:
        logger.exception("审计日志写入失败: action=%s, user=%s", action, user_email)
        session.rollback()
