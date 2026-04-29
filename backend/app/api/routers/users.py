from fastapi import APIRouter

from app.deps import AuditInfo, SessionDep
from app.deps.audit import log_audit
from app.deps.auth import CurrentUser
from app.schemas import Response, UserDetailResp, UserPublicResp, UserUpdateMeReq, UserUpdatePasswordReq
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=Response[UserDetailResp])
def read_user_me(
    current_user: CurrentUser,
    session: SessionDep,
) -> Response[UserDetailResp]:
    """获取当前用户详情，包含角色和权限。"""
    user_detail = user_service.get_user_detail(session=session, user_id=current_user.id)
    return Response.ok(data=user_detail)


@router.patch("/me", response_model=Response[UserPublicResp])
def update_user_me(
    *,
    session: SessionDep,
    user_in: UserUpdateMeReq,
    current_user: CurrentUser,
    audit: AuditInfo,
) -> Response[UserPublicResp]:
    """更新当前用户个人资料。"""
    user = user_service.update_user_me(session=session, user_update=user_in, current_user=current_user)

    log_audit(session, action="更新个人资料", detail=f"姓名: {user_in.full_name}", **audit)

    return Response.ok(data=UserPublicResp.model_validate(user))


@router.patch("/me/password", response_model=Response[None])
def update_password_me(
    *,
    session: SessionDep,
    password_in: UserUpdatePasswordReq,
    current_user: CurrentUser,
    audit: AuditInfo,
) -> Response[None]:
    """修改当前用户密码。"""
    user_service.update_user_password(session=session, password_in=password_in, current_user=current_user)

    log_audit(session, action="修改密码", **audit)

    return Response.ok(data=None, message="密码修改成功")
