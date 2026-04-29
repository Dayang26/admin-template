import uuid

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

from app.models.db.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.db.upload_file import UploadFile


class SystemSetting(UUIDPrimaryKeyMixin, TimestampMixin, SQLModel, table=True):
    __tablename__ = "t_system_setting"  # type: ignore

    setting_key: str = Field(default="default", sa_column=Column(String, unique=True, nullable=False))
    system_name: str = Field(max_length=100)
    tagline: str | None = Field(default=None, max_length=200)
    copyright: str | None = Field(default=None, max_length=255)
    page_title_template: str = Field(max_length=100)

    logo_light_file_id: uuid.UUID | None = Field(default=None, foreign_key="t_upload_file.id", ondelete="SET NULL", nullable=True)
    logo_dark_file_id: uuid.UUID | None = Field(default=None, foreign_key="t_upload_file.id", ondelete="SET NULL", nullable=True)
    favicon_file_id: uuid.UUID | None = Field(default=None, foreign_key="t_upload_file.id", ondelete="SET NULL", nullable=True)
    login_background_file_id: uuid.UUID | None = Field(default=None, foreign_key="t_upload_file.id", ondelete="SET NULL", nullable=True)

    logo_light_file: UploadFile | None = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "SystemSetting.logo_light_file_id==UploadFile.id",
            "lazy": "selectin",
        }
    )
    logo_dark_file: UploadFile | None = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "SystemSetting.logo_dark_file_id==UploadFile.id",
            "lazy": "selectin",
        }
    )
    favicon_file: UploadFile | None = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "SystemSetting.favicon_file_id==UploadFile.id",
            "lazy": "selectin",
        }
    )
    login_background_file: UploadFile | None = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "SystemSetting.login_background_file_id==UploadFile.id",
            "lazy": "selectin",
        }
    )

    primary_color: str = Field(max_length=20)
    theme_mode: str = Field(max_length=20)
    layout_mode: str = Field(max_length=20)

    menu_collapsed_default: bool = Field(default=False)
    fixed_header: bool = Field(default=True)
    fixed_sidebar: bool = Field(default=True)
    page_animation_enabled: bool = Field(default=True)

    default_home_path: str = Field(max_length=255)

    tab_view_enabled: bool = Field(default=False)
    route_cache_enabled: bool = Field(default=False)
    request_timeout_ms: int = Field(default=10000)
