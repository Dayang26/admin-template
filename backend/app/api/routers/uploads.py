from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query
from fastapi import UploadFile as FastAPIUploadFile

from app.deps.audit import AuditInfo, log_audit
from app.deps.auth import CurrentUser
from app.deps.db import SessionDep
from app.deps.permission import require_permission
from app.schemas import Response
from app.schemas.upload import UploadCleanupResp, UploadFileResp, UploadFileType, UploadVisibility
from app.services import upload_service

router = APIRouter(prefix="/uploads", tags=["uploads"])


class UploadPurpose(str, Enum):
    system_setting_logo = "system_setting_logo"
    system_setting_favicon = "system_setting_favicon"
    system_setting_login_background = "system_setting_login_background"


UPLOAD_PURPOSE_PERMISSIONS: dict[str, tuple[str, str]] = {
    "system_setting_logo": ("system_setting", "upload_logo"),
    "system_setting_favicon": ("system_setting", "upload_favicon"),
    "system_setting_login_background": ("system_setting", "upload_login_background"),
}

UPLOAD_PURPOSE_DESCRIPTION = """
上传用途，必填。当前模板内置用途：

- `system_setting_logo`：系统设置 Logo（浅色/深色 Logo 共用），需要 `system_setting:upload_logo`
- `system_setting_favicon`：系统设置 Favicon，需要 `system_setting:upload_favicon`
- `system_setting_login_background`：系统设置登录背景图，需要 `system_setting:upload_login_background`
"""


@router.post(
    "",
    response_model=Response[UploadFileResp],
    status_code=201,
    summary="上传文件",
    description=("通用文件上传入口。模板默认用于系统设置素材上传。调用方必须通过 `purpose` 声明上传用途，后端会按用途校验对应 RBAC 权限。"),
)
def upload_file(
    session: SessionDep,
    current_user: CurrentUser,
    audit_info: AuditInfo,
    file: Annotated[FastAPIUploadFile, File(description="要上传的文件。当前模板只支持图片文件。")],
    file_type: Annotated[str, Form(max_length=50, description="文件类型。当前仅支持 image。")] = UploadFileType.image.value,
    visibility: Annotated[str, Form(max_length=50, description="访问范围。public 会生成 public_url，private 不会公开访问。")] = UploadVisibility.public.value,
    purpose: Annotated[
        UploadPurpose,
        Form(
            description=UPLOAD_PURPOSE_DESCRIPTION,
            examples=["system_setting_logo"],
        ),
    ] = ...,
) -> Response[UploadFileResp]:
    purpose_value = purpose.value
    permission = UPLOAD_PURPOSE_PERMISSIONS.get(purpose_value)
    if not permission:
        raise HTTPException(status_code=400, detail="不支持的上传用途")

    resource, action = permission
    require_permission(resource, action)(session, current_user)

    result = upload_service.process_upload(
        session=session,
        file=file,
        file_type=file_type,
        visibility=visibility,
        purpose=purpose_value,
        created_by_id=current_user.id,
        audit_info=audit_info,
    )
    return Response.ok(data=result, code=201)


@router.delete(
    "/orphans",
    dependencies=[Depends(require_permission("upload", "delete"))],
    response_model=Response[UploadCleanupResp],
    summary="清理孤儿上传文件",
    description="删除未被用户头像或系统设置图片引用，且创建时间早于指定分钟数的上传文件记录及本地文件。",
)
def cleanup_orphan_uploads(
    session: SessionDep,
    audit_info: AuditInfo,
    min_age_minutes: Annotated[int, Query(ge=0, le=60 * 24 * 30, description="只清理至少创建这么多分钟的孤儿文件。")] = 60,
) -> Response[UploadCleanupResp]:
    deleted_file_ids = upload_service.delete_unreferenced_upload_files(
        session=session,
        min_age_minutes=min_age_minutes,
    )
    log_audit(
        session=session,
        action="清理孤儿上传文件",
        detail=f"删除数量: {len(deleted_file_ids)}",
        resource_type="upload_file",
        resource_id="orphans",
        changes={
            "deleted_file_ids": deleted_file_ids,
            "min_age_minutes": min_age_minutes,
        },
        **audit_info,
    )
    return Response.ok(
        data=UploadCleanupResp(
            deleted_count=len(deleted_file_ids),
            deleted_file_ids=deleted_file_ids,
        )
    )
