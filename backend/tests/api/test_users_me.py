from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.conftest import assert_error, assert_success


def test_update_user_me_success(client: TestClient, normal_user_token_headers: dict[str, str], session: Session) -> None:  # noqa: ARG001
    """Test that a logged-in user can update their own full name."""
    payload = {"full_name": "Updated Me Name"}
    response = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json=payload,
    )
    data = assert_success(response)
    assert data["full_name"] == "Updated Me Name"

    # Email should be 'normal@example.com' (from conftest.py)
    assert data["email"] == "normal@example.com"


def test_update_user_me_no_email_update(client: TestClient, normal_user_token_headers: dict[str, str], session: Session) -> None:  # noqa: ARG001
    """Test that updating email is NOT allowed (it should be ignored or not present in schema)."""
    # If the schema doesn't have email, it will be ignored by Pydantic
    payload = {"full_name": "New Name", "email": "hacker@example.com"}
    response = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json=payload,
    )
    data = assert_success(response)
    assert data["full_name"] == "New Name"
    # Email should remain 'normal@example.com' (from conftest.py)
    assert data["email"] == "normal@example.com"


def test_update_user_me_unauthorized(client: TestClient) -> None:
    """Test that accessing /me without token returns 401."""
    payload = {"full_name": "New Name"}
    response = client.patch(
        f"{settings.API_V1_STR}/users/me",
        json=payload,
    )
    assert_error(response, 401)


def test_read_user_me_success(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    """Test that a logged-in user can fetch their own details."""
    response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
    )
    data = assert_success(response)
    assert data["email"] == "normal@example.com"
    assert "roles" in data
    assert "class_memberships" in data


def test_update_password_me_success(client: TestClient, normal_user_token_headers: dict[str, str], session: Session) -> None:  # noqa: ARG001
    """Test that a logged-in user can update their own password."""
    payload = {
        "current_password": "password1234",  # from conftest.py
        "new_password": "newpassword1234",
    }
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=normal_user_token_headers,
        json=payload,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "密码修改成功"


def test_update_password_me_incorrect_current(client: TestClient, normal_user_token_headers: dict[str, str], session: Session) -> None:  # noqa: ARG001
    """Test updating password with wrong current password."""
    payload = {
        "current_password": "wrongpassword",
        "new_password": "newpassword1234",
    }
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=normal_user_token_headers,
        json=payload,
    )
    assert_error(response, 400, "Incorrect current password")


def test_update_password_me_too_short(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    """Test updating password with a too short new password."""
    payload = {
        "current_password": "password1234",
        "new_password": "short",
    }
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=normal_user_token_headers,
        json=payload,
    )
    # FastAPI returns 422 for pydantic validation errors
    assert response.status_code == 422
    assert response.json()["message"] == "Validation Error"


def test_update_password_me_too_long(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    """Test updating password with a too long new password."""
    payload = {
        "current_password": "password1234",
        "new_password": "a" * 129,
    }
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=normal_user_token_headers,
        json=payload,
    )
    assert response.status_code == 422
