import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    email: EmailStr = Field(max_length=255)
    is_active: bool = True
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserCreateByAdmin(UserBase):
    password: str = Field(min_length=8, max_length=128)
    roles: list[str] = Field(min_length=1, description="List of role names to assign")


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class UserUpdateReq(SQLModel):
    """Request schema for updating a user by admin."""

    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = Field(default=None)
    roles: list[str] | None = Field(default=None, min_length=1, description="List of role names to assign (replace mode)")
