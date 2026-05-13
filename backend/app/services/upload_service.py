import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from fastapi import HTTPException
from fastapi import UploadFile as FastAPIUploadFile
from sqlalchemy import or_
from sqlmodel import Session, select

from app.core.config import settings
from app.models.db import SystemSetting, UploadFile, User
from app.schemas.upload import UploadFileResp, UploadFileType, UploadVisibility
from app.services.storage.local import LocalStorageProvider

if TYPE_CHECKING:
    from app.deps.audit import AuditInfo

storage_provider = LocalStorageProvider()
logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "png": {"image/png"},
    "jpg": {"image/jpeg"},
    "jpeg": {"image/jpeg"},
    "webp": {"image/webp"},
    "ico": {"image/x-icon", "image/vnd.microsoft.icon"},
}

FILE_SIGNATURES = {
    "png": b"\x89PNG\r\n\x1a\n",
    "jpeg": b"\xff\xd8\xff",
    "jpg": b"\xff\xd8\xff",
    "webp": b"RIFF",  # We'll check RIFF and WEBP
    "ico": b"\x00\x00\x01\x00",
}


def _verify_image_file(file: FastAPIUploadFile) -> tuple[str, str]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")
    if len(file.filename) > 255:
        raise HTTPException(status_code=400, detail="Filename too long. Max length is 255")

    parts = file.filename.rsplit(".", 1)
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Extension missing")

    extension = parts[-1].lower()
    allowed_exts = [e.strip() for e in settings.UPLOAD_ALLOWED_IMAGE_EXTENSIONS.split(",")]
    if extension not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Extension not allowed. Allowed: {settings.UPLOAD_ALLOWED_IMAGE_EXTENSIONS}")
    if extension not in ALLOWED_MIME_TYPES or extension not in FILE_SIGNATURES:
        raise HTTPException(status_code=400, detail="Unsupported image extension")

    if file.content_type not in ALLOWED_MIME_TYPES[extension]:
        raise HTTPException(status_code=400, detail=f"Invalid MIME type for .{extension}")

    # verify header
    header = file.file.read(12)
    file.file.seek(0)

    if extension in ["jpg", "jpeg"] and not header.startswith(FILE_SIGNATURES["jpg"]):
        raise HTTPException(status_code=400, detail="Invalid image file signature for jpeg")
    elif extension == "png" and not header.startswith(FILE_SIGNATURES["png"]):
        raise HTTPException(status_code=400, detail="Invalid image file signature for png")
    elif extension == "ico" and not header.startswith(FILE_SIGNATURES["ico"]):
        raise HTTPException(status_code=400, detail="Invalid image file signature for ico")
    elif extension == "webp" and not (header.startswith(FILE_SIGNATURES["webp"]) and header[8:12] == b"WEBP"):
        raise HTTPException(status_code=400, detail="Invalid image file signature for webp")

    return extension, file.content_type


def process_upload(
    session: Session,
    file: FastAPIUploadFile,
    file_type: str,
    visibility: str,
    purpose: str | None,
    created_by_id: uuid.UUID,
    audit_info: "AuditInfo",
    log_upload_audit: bool = True,
) -> UploadFileResp:
    if file_type != UploadFileType.image.value:
        raise HTTPException(status_code=400, detail="Only image upload is supported")

    if visibility not in [UploadVisibility.public.value, UploadVisibility.private.value]:
        raise HTTPException(status_code=400, detail="Invalid visibility")
    if purpose is not None and len(purpose) > 100:
        raise HTTPException(status_code=400, detail="Purpose too long. Max length is 100")

    extension, verified_content_type = _verify_image_file(file)

    max_size_bytes = settings.UPLOAD_MAX_IMAGE_SIZE_MB * 1024 * 1024

    stored_file = storage_provider.save(
        file=file,
        visibility=visibility,
        extension=extension,
        max_size_bytes=max_size_bytes,
    )

    try:
        db_obj = UploadFile(
            original_filename=file.filename or "unknown",
            stored_filename=stored_file.storage_key.split("/")[-1],
            extension=extension,
            content_type=verified_content_type,
            size_bytes=stored_file.size_bytes,
            sha256=stored_file.sha256,
            file_type=file_type,
            visibility=visibility,
            storage_provider=stored_file.storage_provider,
            storage_key=stored_file.storage_key,
            public_url=stored_file.public_url,
            purpose=purpose,
            created_by_id=created_by_id,
        )

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
    except Exception:
        session.rollback()
        try:
            storage_provider.delete(visibility=visibility, storage_key=stored_file.storage_key)
        except Exception:
            logger.exception("Failed to delete orphan uploaded file: %s", stored_file.storage_key)
        raise

    if log_upload_audit:
        from app.deps.audit import log_audit

        log_audit(
            session=session,
            action="上传文件",
            detail=f"文件: {file.filename}, 类型: {file_type}, 可见性: {visibility}, 大小: {stored_file.size_bytes}",
            resource_type="upload_file",
            resource_id=db_obj.id,
            changes={
                "original_filename": db_obj.original_filename,
                "file_type": db_obj.file_type,
                "visibility": db_obj.visibility,
                "size_bytes": db_obj.size_bytes,
                "purpose": db_obj.purpose,
            },
            **audit_info,
        )

    return UploadFileResp.model_validate(db_obj)


def delete_upload_file(session: Session, upload_file: UploadFile) -> None:
    visibility = upload_file.visibility
    storage_key = upload_file.storage_key
    session.delete(upload_file)
    session.commit()
    try:
        storage_provider.delete(visibility=visibility, storage_key=storage_key)
    except Exception:
        logger.warning("DB record deleted but failed to remove physical file: %s", storage_key, exc_info=True)


def is_upload_file_referenced(session: Session, upload_file_id: uuid.UUID) -> bool:
    user_ref = session.exec(select(User.id).where(User.avatar_file_id == upload_file_id)).first()
    if user_ref is not None:
        return True

    system_setting_ref = session.exec(
        select(SystemSetting.id).where(
            or_(
                SystemSetting.logo_light_file_id == upload_file_id,
                SystemSetting.logo_dark_file_id == upload_file_id,
                SystemSetting.favicon_file_id == upload_file_id,
                SystemSetting.login_background_file_id == upload_file_id,
            )
        )
    ).first()
    return system_setting_ref is not None


def delete_upload_file_if_unreferenced(session: Session, upload_file_id: uuid.UUID) -> bool:
    upload_file = session.get(UploadFile, upload_file_id)
    if not upload_file or is_upload_file_referenced(session, upload_file_id):
        return False

    delete_upload_file(session=session, upload_file=upload_file)
    return True


def cleanup_upload_file_if_unreferenced(session: Session, upload_file_id: uuid.UUID) -> bool:
    try:
        return delete_upload_file_if_unreferenced(session=session, upload_file_id=upload_file_id)
    except Exception:
        session.rollback()
        logger.exception("Failed to cleanup unreferenced upload file: %s", upload_file_id)
        return False


def delete_unreferenced_upload_files(session: Session, *, min_age_minutes: int) -> list[uuid.UUID]:
    cutoff = datetime.now(UTC) - timedelta(minutes=min_age_minutes)
    candidates = session.exec(select(UploadFile).where(UploadFile.created_at <= cutoff)).all()

    deleted_file_ids: list[uuid.UUID] = []
    for upload_file in candidates:
        if is_upload_file_referenced(session, upload_file.id):
            continue

        upload_file_id = upload_file.id
        try:
            delete_upload_file(session=session, upload_file=upload_file)
            deleted_file_ids.append(upload_file_id)
        except Exception:
            session.rollback()
            logger.exception("Failed to delete orphan upload file: %s", upload_file_id)

    return deleted_file_ids
