import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index
from sqlmodel import Field

from app.models.db.base import UUIDPrimaryKeyMixin, utcnow


class AuditLog(UUIDPrimaryKeyMixin, table=True):
    __tablename__ = "t_audit_log"

    created_at: datetime = Field(
        default_factory=utcnow,
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    user_id: uuid.UUID | None = Field(default=None, index=True)
    user_email: str = Field(max_length=255)
    method: str = Field(max_length=10)  # POST / PATCH / PUT / DELETE
    path: str = Field(max_length=500)
    action: str = Field(max_length=100)  # 中文操作描述
    detail: str | None = Field(default=None, max_length=2000)
    status_code: int = Field(default=200)
    ip_address: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None, max_length=500)

    __table_args__ = (
        Index("ix_audit_log_created_at", "created_at"),
        Index("ix_audit_log_action", "action"),
    )
