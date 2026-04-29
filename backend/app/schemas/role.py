import uuid

from pydantic import ConfigDict, field_validator
from sqlmodel import Field, SQLModel


class RolePermissionUpdateReq(SQLModel):
    model_config = ConfigDict(extra="forbid")

    permission_ids: list[uuid.UUID] = Field(default_factory=list)

    @field_validator("permission_ids")
    @classmethod
    def deduplicate_permission_ids(cls, permission_ids: list[uuid.UUID]) -> list[uuid.UUID]:
        unique_permission_ids: list[uuid.UUID] = []
        seen: set[uuid.UUID] = set()
        for permission_id in permission_ids:
            if permission_id in seen:
                continue
            unique_permission_ids.append(permission_id)
            seen.add(permission_id)
        return unique_permission_ids
