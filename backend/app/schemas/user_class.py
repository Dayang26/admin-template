import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class ClassBase(SQLModel):
    name: str = Field(max_length=100, description="班级名称")
    description: str | None = Field(default=None, max_length=500, description="班级描述")


class ClassCreateReq(ClassBase):
    pass


class ClassUpdateReq(SQLModel):
    name: str | None = Field(default=None, max_length=100, description="班级名称")
    description: str | None = Field(default=None, max_length=500, description="班级描述")


class ClassPublicResp(ClassBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
