import uuid
from datetime import datetime, timedelta, timezone

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_now_local() -> datetime:
    return datetime.now(timezone(timedelta(hours=8)))


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Database model
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_now_local,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


class UserCreateReq(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserPublicResp(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None
