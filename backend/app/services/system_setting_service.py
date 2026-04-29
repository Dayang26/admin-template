import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.deps.audit import AuditInfo, log_audit
from app.models.db import SystemSetting, UploadFile
from app.schemas.system_setting import (
    SystemSettingAdminResp,
    SystemSettingPublicResp,
    SystemSettingUpdateReq,
)


def get_or_create_system_setting(session: Session) -> SystemSetting:
    setting = session.exec(select(SystemSetting).where(SystemSetting.setting_key == "default")).first()
    if not setting:
        setting = SystemSetting(
            setting_key="default",
            system_name="Carrier Agent",
            tagline="管理后台",
            page_title_template="{page} - {systemName}",
        )
        session.add(setting)
        session.commit()
        session.refresh(setting)
    return setting


def _build_public_resp(setting: SystemSetting) -> SystemSettingPublicResp:
    return SystemSettingPublicResp(
        system_name=setting.system_name,
        tagline=setting.tagline,
        copyright=setting.copyright,
        page_title_template=setting.page_title_template,
        logo_light_url=setting.logo_light_file.public_url if setting.logo_light_file else None,
        logo_dark_url=setting.logo_dark_file.public_url if setting.logo_dark_file else None,
        favicon_url=setting.favicon_file.public_url if setting.favicon_file else None,
        login_background_url=setting.login_background_file.public_url if setting.login_background_file else None,
    )


def _build_admin_resp(setting: SystemSetting) -> SystemSettingAdminResp:
    public_resp = _build_public_resp(setting)
    return SystemSettingAdminResp(
        **public_resp.model_dump(),
        logo_light_file_id=setting.logo_light_file_id,
        logo_dark_file_id=setting.logo_dark_file_id,
        favicon_file_id=setting.favicon_file_id,
        login_background_file_id=setting.login_background_file_id,
    )


def get_public_system_setting(session: Session) -> SystemSettingPublicResp:
    setting = get_or_create_system_setting(session)
    return _build_public_resp(setting)


def get_admin_system_setting(session: Session) -> SystemSettingAdminResp:
    setting = get_or_create_system_setting(session)
    return _build_admin_resp(setting)


def _validate_public_image_file(session: Session, file_id: uuid.UUID, field_name: str) -> None:
    upload_file = session.get(UploadFile, file_id)
    if not upload_file:
        raise HTTPException(status_code=400, detail=f"{field_name}: 文件不存在")
    if upload_file.file_type != "image":
        raise HTTPException(status_code=400, detail=f"{field_name}: 只能绑定图片文件")
    if upload_file.visibility != "public":
        raise HTTPException(status_code=400, detail=f"{field_name}: 只能绑定公开文件")
    if not upload_file.public_url:
        raise HTTPException(status_code=400, detail=f"{field_name}: 文件没有公开访问 URL")


def update_system_setting(
    session: Session,
    settings_update: SystemSettingUpdateReq,
    audit_info: AuditInfo,
) -> SystemSettingAdminResp:
    setting = get_or_create_system_setting(session)

    update_data = settings_update.model_dump(exclude_unset=True)
    if not update_data:
        return _build_admin_resp(setting)

    # 校验文件字段
    file_fields = {
        "logo_light_file_id": "浅色 Logo",
        "logo_dark_file_id": "深色 Logo",
        "favicon_file_id": "Favicon",
        "login_background_file_id": "登录页背景图",
    }
    for field_id, field_name in file_fields.items():
        val = update_data.get(field_id)
        if val is not None:
            _validate_public_image_file(session, val, field_name)

    # Apply updates
    for k, v in update_data.items():
        setattr(setting, k, v)

    session.add(setting)
    session.commit()
    session.refresh(setting)

    changes = list(update_data.keys())
    log_audit(
        session,
        action="更新系统设置",
        detail=f"变更字段: {', '.join(changes)}",
        **audit_info,
    )

    return _build_admin_resp(setting)
