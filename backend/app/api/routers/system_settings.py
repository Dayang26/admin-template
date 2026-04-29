from fastapi import APIRouter

from app.deps.db import SessionDep
from app.schemas import Response
from app.schemas.system_setting import SystemSettingPublicResp
from app.services import system_setting_service

router = APIRouter(prefix="/system-settings", tags=["system_settings"])


@router.get("/public", response_model=Response[SystemSettingPublicResp])
def get_public_system_settings(session: SessionDep) -> Response[SystemSettingPublicResp]:
    """获取公开可访问的系统设置（供前端登录页、全局 UI 渲染等使用）。"""
    result = system_setting_service.get_public_system_setting(session=session)
    return Response.ok(data=result)
