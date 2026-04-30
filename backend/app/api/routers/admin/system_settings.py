from fastapi import APIRouter, Depends

from app.deps.audit import AuditInfo
from app.deps.auth import CurrentUser
from app.deps.db import SessionDep
from app.deps.permission import require_permission
from app.schemas import Response
from app.schemas.system_setting import SystemSettingAdminResp, SystemSettingUpdateReq
from app.services import system_setting_service

router = APIRouter(prefix="/admin/system-settings", tags=["admin"])

SYSTEM_SETTING_FIELD_PERMISSIONS: dict[str, str] = {
    "system_name": "update_system_name",
    "tagline": "update_tagline",
    "copyright": "update_copyright",
    "page_title_template": "update_page_title_template",
    "logo_light_file_id": "upload_logo",
    "logo_dark_file_id": "upload_logo",
    "favicon_file_id": "upload_favicon",
    "login_background_file_id": "upload_login_background",
}


@router.get("", dependencies=[Depends(require_permission("system_setting", "read"))], response_model=Response[SystemSettingAdminResp])
def get_admin_system_settings(session: SessionDep) -> Response[SystemSettingAdminResp]:
    """获取管理后台用的系统配置（包含文件 ID 等信息）。"""
    result = system_setting_service.get_admin_system_setting(session=session)
    return Response.ok(data=result)


@router.patch("", dependencies=[Depends(require_permission("system_setting", "read"))], response_model=Response[SystemSettingAdminResp])
def update_admin_system_settings(
    session: SessionDep,
    current_user: CurrentUser,
    settings_update: SystemSettingUpdateReq,
    audit_info: AuditInfo,
) -> Response[SystemSettingAdminResp]:
    """修改系统设置。"""
    required_actions = {action for field_name, action in SYSTEM_SETTING_FIELD_PERMISSIONS.items() if field_name in settings_update.model_fields_set}
    for action in sorted(required_actions):
        require_permission("system_setting", action)(session, current_user)

    result = system_setting_service.update_system_setting(
        session=session,
        settings_update=settings_update,
        audit_info=audit_info,
    )
    return Response.ok(data=result)
