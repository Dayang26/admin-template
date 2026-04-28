from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.core import security
from app.core.config import settings
from app.deps import SessionDep
from app.deps.audit import log_audit
from app.schemas.token import TokenResp
from app.services import login_service

router = APIRouter(tags=["login"])


@router.post("/login/access-token", response_model=TokenResp)
def login_access_token(
    session: SessionDep,
    request: Request,
    from_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenResp:
    user = login_service.authenticate(session=session, email=from_data.username, password=from_data.password)

    if not user:
        raise HTTPException(status_code=400, detail="邮箱或密码错误")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="该账号已被禁用")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = TokenResp(
        access_token=security.create_access_token(user.id, expires_delta=access_token_expires),
    )

    # 记录登录日志
    forwarded = request.headers.get("x-forwarded-for")
    ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else None)
    log_audit(
        session,
        action="用户登录",
        detail=f"邮箱: {from_data.username}",
        user_id=user.id,
        user_email=user.email,
        method="POST",
        path="/api/v1/login/access-token",
        ip_address=ip,
        user_agent=request.headers.get("user-agent", "")[:500],
    )

    return token
