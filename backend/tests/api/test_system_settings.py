from fastapi.testclient import TestClient

from app.core.config import settings


def test_get_public_system_settings(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/system-settings/public")
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["system_name"] == "Carrier Agent"
    assert data["tagline"] == "管理后台"
    assert "logo_light_file_id" not in data  # 应该被隔离不暴露给前台
