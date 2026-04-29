from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models.db import User
from tests.conftest import assert_error, assert_success


def test_get_dashboard_stats_success(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    # 保证数据库里有一些数据
    session.add(User(email="dash1@example.com", hashed_password="pw"))
    session.commit()

    response = client.get(f"{settings.API_V1_STR}/admin/dashboard/stats", headers=superuser_token_headers)
    data = assert_success(response)
    assert data["total_users"] >= 1
    assert "role_distribution" in data


def test_get_dashboard_stats_forbidden(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    response = client.get(f"{settings.API_V1_STR}/admin/dashboard/stats", headers=normal_user_token_headers)
    assert_error(response, 403)
