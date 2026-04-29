import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    email: EmailStr = Field(max_length=255)
    is_active: bool = True
    full_name: str | None = Field(default=None, max_length=255)


class UserCreateReq(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserCreateByAdminReq(UserBase):
    password: str = Field(min_length=8, max_length=128)
    roles: list[str] = Field(min_length=1, description="List of role names to assign")


class UserPublicResp(UserBase):
    id: uuid.UUID
    created_at: datetime


class UserPublicWithRolesResp(UserPublicResp):
    """用户列表响应，包含全局角色名"""

    roles: list[str] = Field(default_factory=list)


class UsersPublicResp(SQLModel):
    data: list[UserPublicResp]
    count: int


class UserUpdateReq(SQLModel):
    """Request schema for updating a user by admin."""

    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = Field(default=None)
    roles: list[str] | None = Field(default=None, min_length=1, description="List of role names to assign (replace mode)")


class UserUpdateMeReq(SQLModel):
    """Request schema for updating own profile."""

    full_name: str | None = Field(default=None, max_length=255)


class UserUpdatePasswordReq(SQLModel):
    """用户修改密码请求"""

    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserDetailResp(UserPublicResp):
    """用户详情，包含角色与权限"""

    roles: list[str]
    permissions: list[str] = Field(default_factory=list)  # 权限列表，如 ["user:read"]
