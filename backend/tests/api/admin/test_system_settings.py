from fastapi.testclient import TestClient

from app.core.config import settings
from tests.conftest import assert_error, assert_success


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
    payload = {"system_name": "New System Name", "primary_color": "#112233"}
    response = client.patch(f"{settings.API_V1_STR}/admin/system-settings", headers=superuser_token_headers, json=payload)
    data = assert_success(response, 200)

    assert data["system_name"] == "New System Name"
    assert data["primary_color"] == "#112233"

    # Verify public settings are also updated
    public_response = client.get(f"{settings.API_V1_STR}/system-settings/public")
    assert public_response.json()["data"]["system_name"] == "New System Name"


def test_update_admin_system_settings_invalid_image(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    import uuid

    invalid_uuid = str(uuid.uuid4())
    payload = {"logo_light_file_id": invalid_uuid}
    response = client.patch(f"{settings.API_V1_STR}/admin/system-settings", headers=superuser_token_headers, json=payload)
    assert_error(response, 400, "浅色 Logo: 文件不存在")
