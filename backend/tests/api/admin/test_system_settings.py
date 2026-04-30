import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models.db import Permission, Role, RolePermission, User, UserRole
from tests.conftest import assert_error, assert_success


def _headers_for_permissions(session: Session, permissions: list[tuple[str, str]]) -> dict[str, str]:
    role = Role(name=f"system_setting_role_{uuid.uuid4().hex[:8]}", description="System setting test role")
    user = User(
        email=f"system_setting_user_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=get_password_hash("password1234"),
        is_active=True,
    )
    session.add(role)
    session.add(user)
    session.commit()
    session.refresh(role)
    session.refresh(user)

    for resource, action in permissions:
        permission = session.exec(select(Permission).where(Permission.resource == resource, Permission.action == action)).one()
        session.add(RolePermission(role_id=role.id, permission_id=permission.id))
    session.add(UserRole(user_id=user.id, role_id=role.id))
    session.commit()

    return {"Authorization": f"Bearer {create_access_token(subject=user.id)}"}


def test_get_admin_system_settings_unauthorized(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/admin/system-settings")
    assert response.status_code == 401


def test_get_admin_system_settings_forbidden(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    response = client.get(f"{settings.API_V1_STR}/admin/system-settings", headers=normal_user_token_headers)
    assert response.status_code == 403


def test_get_admin_system_settings_success(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    response = client.get(f"{settings.API_V1_STR}/admin/system-settings", headers=superuser_token_headers)
    data = assert_success(response, 200)

    assert data["system_name"] == "Carrier Agent"
    assert "logo_light_file_id" in data


def test_update_admin_system_settings_success(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    payload = {
        "system_name": "New System Name",
        "tagline": "New tagline",
        "page_title_template": "{page} | {systemName}",
    }
    response = client.patch(f"{settings.API_V1_STR}/admin/system-settings", headers=superuser_token_headers, json=payload)
    data = assert_success(response, 200)

    assert data["system_name"] == "New System Name"
    assert data["tagline"] == "New tagline"
    assert data["page_title_template"] == "{page} | {systemName}"

    # Verify public settings are also updated
    public_response = client.get(f"{settings.API_V1_STR}/system-settings/public")
    assert public_response.json()["data"]["system_name"] == "New System Name"


def test_update_admin_system_settings_forbidden_without_field_permission(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    payload = {"system_name": "Unauthorized Name"}
    response = client.patch(f"{settings.API_V1_STR}/admin/system-settings", headers=normal_user_token_headers, json=payload)
    assert_error(response, 403)


def test_update_admin_system_settings_checks_each_field_permission(client: TestClient, session: Session) -> None:
    headers = _headers_for_permissions(
        session,
        [
            ("system_setting", "read"),
            ("system_setting", "update_system_name"),
        ],
    )

    allowed_response = client.patch(
        f"{settings.API_V1_STR}/admin/system-settings",
        headers=headers,
        json={"system_name": "Allowed Name"},
    )
    data = assert_success(allowed_response, 200)
    assert data["system_name"] == "Allowed Name"

    forbidden_response = client.patch(
        f"{settings.API_V1_STR}/admin/system-settings",
        headers=headers,
        json={"system_name": "Allowed Name 2", "tagline": "Forbidden tagline"},
    )
    assert_error(forbidden_response, 403)


def test_update_admin_system_settings_invalid_image(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    import uuid

    invalid_uuid = str(uuid.uuid4())
    payload = {"logo_light_file_id": invalid_uuid}
    response = client.patch(f"{settings.API_V1_STR}/admin/system-settings", headers=superuser_token_headers, json=payload)
    assert_error(response, 400, "浅色 Logo: 文件不存在")


def test_update_admin_system_settings_rejects_null_required_field(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    payload = {"system_name": None}
    response = client.patch(f"{settings.API_V1_STR}/admin/system-settings", headers=superuser_token_headers, json=payload)
    assert_error(response, 422)


def test_update_admin_system_settings_rejects_removed_behavior_fields(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    payload = {"primary_color": "#112233"}
    response = client.patch(f"{settings.API_V1_STR}/admin/system-settings", headers=superuser_token_headers, json=payload)
    assert_error(response, 422)
