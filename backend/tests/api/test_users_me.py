from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models.db import User
from tests.conftest import assert_success, assert_error


def test_update_user_me_success(client: TestClient, normal_user_token_headers: dict[str, str], session: Session) -> None:
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


def test_update_user_me_no_email_update(client: TestClient, normal_user_token_headers: dict[str, str], session: Session) -> None:
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
