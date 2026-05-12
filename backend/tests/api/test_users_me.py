from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models.db import UploadFile, User
from tests.conftest import assert_error, assert_success


@pytest.fixture()
def isolate_avatar_upload_dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "UPLOAD_PUBLIC_DIR", str(tmp_path / "public"))
    monkeypatch.setattr(settings, "UPLOAD_PRIVATE_DIR", str(tmp_path / "private"))


def _png_content() -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 10


def _saved_files(root: Path) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_file()]


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
    assert "permissions" in data


def test_read_user_me_rejects_token_after_admin_disables_user(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    superuser_token_headers: dict[str, str],
    session: Session,
) -> None:
    """A token issued before the user is disabled must stop working."""
    current_user = session.exec(select(User).where(User.email == "normal@example.com")).first()
    assert current_user is not None

    disable_response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{current_user.id}",
        headers=superuser_token_headers,
        json={"is_active": False},
    )
    assert_success(disable_response)

    response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
    )

    assert_error(response, 403, "该账号已被禁用")


def test_upload_user_avatar_success(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    session: Session,
    tmp_path: Path,
    isolate_avatar_upload_dirs: None,
) -> None:
    assert isolate_avatar_upload_dirs is None
    response = client.post(
        f"{settings.API_V1_STR}/users/me/avatar",
        headers=normal_user_token_headers,
        files={"file": ("avatar.png", _png_content(), "image/png")},
    )
    data = assert_success(response)
    assert data["avatar_file_id"] is not None
    assert data["avatar_url"].startswith("/uploads/public/")

    current_user = session.exec(select(User).where(User.email == "normal@example.com")).first()
    assert current_user is not None
    assert current_user.avatar_file_id is not None

    upload_file = session.get(UploadFile, current_user.avatar_file_id)
    assert upload_file is not None
    assert upload_file.purpose == "user_avatar"
    assert _saved_files(tmp_path / "public")


def test_replace_user_avatar_cleans_previous_upload(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    session: Session,
    tmp_path: Path,
    isolate_avatar_upload_dirs: None,
) -> None:
    assert isolate_avatar_upload_dirs is None
    first_response = client.post(
        f"{settings.API_V1_STR}/users/me/avatar",
        headers=normal_user_token_headers,
        files={"file": ("avatar-1.png", _png_content(), "image/png")},
    )
    first_data = assert_success(first_response)

    second_response = client.post(
        f"{settings.API_V1_STR}/users/me/avatar",
        headers=normal_user_token_headers,
        files={"file": ("avatar-2.png", _png_content(), "image/png")},
    )
    second_data = assert_success(second_response)

    assert second_data["avatar_file_id"] != first_data["avatar_file_id"]
    assert session.get(UploadFile, first_data["avatar_file_id"]) is None
    assert session.get(UploadFile, second_data["avatar_file_id"]) is not None
    assert len(_saved_files(tmp_path / "public")) == 1


def test_remove_user_avatar_success(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    session: Session,
    tmp_path: Path,
    isolate_avatar_upload_dirs: None,
) -> None:
    assert isolate_avatar_upload_dirs is None
    upload_response = client.post(
        f"{settings.API_V1_STR}/users/me/avatar",
        headers=normal_user_token_headers,
        files={"file": ("avatar.png", _png_content(), "image/png")},
    )
    uploaded_data = assert_success(upload_response)

    remove_response = client.delete(
        f"{settings.API_V1_STR}/users/me/avatar",
        headers=normal_user_token_headers,
    )
    removed_data = assert_success(remove_response)

    assert removed_data["avatar_file_id"] is None
    assert removed_data["avatar_url"] is None
    assert session.get(UploadFile, uploaded_data["avatar_file_id"]) is None
    assert _saved_files(tmp_path / "public") == []


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
