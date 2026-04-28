import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class ClassMemberResp(SQLModel):
    """班级成员信息"""

    user_id: uuid.UUID
    email: str
    full_name: str | None
    role: str  # 在该班级中的角色
    joined_at: datetime  # UserRole.created_at


class ClassMemberAddReq(SQLModel):
    """分配用户到班级"""

    user_id: uuid.UUID
    role: str = Field(description="在该班级中的角色，如 teacher / student")
