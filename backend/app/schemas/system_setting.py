import uuid

from pydantic import ConfigDict, Field, model_validator
from sqlmodel import SQLModel


class SystemSettingPublicResp(SQLModel):
    system_name: str
    tagline: str | None
    copyright: str | None
    page_title_template: str

    logo_light_url: str | None
    logo_dark_url: str | None
    favicon_url: str | None
    login_background_url: str | None


class SystemSettingAdminResp(SystemSettingPublicResp):
    logo_light_file_id: uuid.UUID | None
    logo_dark_file_id: uuid.UUID | None
    favicon_file_id: uuid.UUID | None
    login_background_file_id: uuid.UUID | None


class SystemSettingUpdateReq(SQLModel):
    model_config = ConfigDict(extra="forbid")

    system_name: str | None = Field(default=None, min_length=1, max_length=100, description="系统名称，不能为空")
    tagline: str | None = Field(default=None, max_length=200, description="系统标语")
    copyright: str | None = Field(default=None, max_length=200, description="版权信息")
    page_title_template: str | None = Field(default=None, min_length=1, max_length=100, description="页面标题模板")

    logo_light_file_id: uuid.UUID | None = None
    logo_dark_file_id: uuid.UUID | None = None
    favicon_file_id: uuid.UUID | None = None
    login_background_file_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "SystemSettingUpdateReq":
        required_fields = {"system_name", "page_title_template"}
        for field_name in required_fields:
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self
