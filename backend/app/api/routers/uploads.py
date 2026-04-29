from typing import Annotated

from fastapi import APIRouter, Depends, File, Form
from fastapi import UploadFile as FastAPIUploadFile

from app.deps.audit import AuditInfo
from app.deps.auth import CurrentUser
from app.deps.db import SessionDep
from app.deps.permission import require_permission
from app.schemas import Response
from app.schemas.upload import UploadFileResp, UploadFileType, UploadVisibility
from app.services import upload_service

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post(
    "",
    response_model=Response[UploadFileResp],
    status_code=201,
    dependencies=[Depends(require_permission("upload", "create"))],
)
def upload_file(
    session: SessionDep,
    current_user: CurrentUser,
    audit_info: AuditInfo,
    file: Annotated[FastAPIUploadFile, File(...)],
    file_type: Annotated[str, Form(max_length=50)] = UploadFileType.image.value,
    visibility: Annotated[str, Form(max_length=50)] = UploadVisibility.public.value,
    purpose: Annotated[str | None, Form(max_length=100)] = None,
) -> Response[UploadFileResp]:
    result = upload_service.process_upload(
        session=session,
        file=file,
        file_type=file_type,
        visibility=visibility,
        purpose=purpose,
        created_by_id=current_user.id,
        audit_info=audit_info,
    )
    return Response.ok(data=result, code=201)
