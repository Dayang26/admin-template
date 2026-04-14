import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UUIDPrimaryKeyMixin(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": func.now()},
        nullable=False,
    )
