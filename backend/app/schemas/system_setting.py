import uuid
from typing import Literal

from pydantic import Field
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

    primary_color: str
    theme_mode: str
    layout_mode: str

    menu_collapsed_default: bool
    fixed_header: bool
    fixed_sidebar: bool
    page_animation_enabled: bool

    default_home_path: str


class SystemSettingAdminResp(SystemSettingPublicResp):
    logo_light_file_id: uuid.UUID | None
    logo_dark_file_id: uuid.UUID | None
    favicon_file_id: uuid.UUID | None
    login_background_file_id: uuid.UUID | None

    tab_view_enabled: bool
    route_cache_enabled: bool
    request_timeout_ms: int


class SystemSettingUpdateReq(SQLModel):
    system_name: str | None = Field(default=None, min_length=1, max_length=100, description="系统名称，不能为空")
    tagline: str | None = Field(default=None, max_length=200, description="系统标语")
    copyright: str | None = Field(default=None, max_length=200, description="版权信息")
    page_title_template: str | None = Field(default=None, min_length=1, max_length=100, description="页面标题模板")

    logo_light_file_id: uuid.UUID | None = None
    logo_dark_file_id: uuid.UUID | None = None
    favicon_file_id: uuid.UUID | None = None
    login_background_file_id: uuid.UUID | None = None

    primary_color: str | None = Field(default=None, pattern=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", description="系统主色调，必须为合法的十六进制颜色代码")
    theme_mode: Literal["light", "dark", "system"] | None = None
    layout_mode: Literal["sidebar", "top", "mixed"] | None = None

    menu_collapsed_default: bool | None = None
    fixed_header: bool | None = None
    fixed_sidebar: bool | None = None
    page_animation_enabled: bool | None = None

    default_home_path: str | None = Field(default=None, min_length=1, max_length=200, pattern=r"^\/", description="默认首页路径，必须以 / 开头")

    tab_view_enabled: bool | None = None
    route_cache_enabled: bool | None = None
    request_timeout_ms: int | None = Field(default=None, ge=1000, le=60000, description="请求超时时间，范围在 1000ms 到 60000ms 之间")
