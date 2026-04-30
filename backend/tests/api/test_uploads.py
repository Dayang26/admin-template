import uuid
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.main import mount_public_uploads
from app.models.db import Permission, Role, RolePermission, UploadFile, User, UserRole
from tests.conftest import assert_success


@pytest.fixture(autouse=True)
def isolate_upload_dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "UPLOAD_PUBLIC_DIR", str(tmp_path / "public"))
    monkeypatch.setattr(settings, "UPLOAD_PRIVATE_DIR", str(tmp_path / "private"))


def _png_content() -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 10


def _jpg_content() -> bytes:
    return b"\xff\xd8\xff" + b"\x00" * 10


def _saved_files(root: Path) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_file()]


def test_upload_image_success(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    files = {"file": ("test.png", _png_content(), "image/png")}
    data = {"file_type": "image", "visibility": "public", "purpose": "system_setting_logo"}

    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=superuser_token_headers,
        files=files,
        data=data,
    )
    assert response.status_code == 201
    resp = response.json()
    assert resp["code"] == 201
    assert resp["data"]["original_filename"] == "test.png"
    assert resp["data"]["public_url"].startswith("/uploads/public/")


def test_upload_image_unauthorized(client: TestClient) -> None:
    files = {"file": ("test.png", _png_content(), "image/png")}
    data = {"file_type": "image", "visibility": "public", "purpose": "system_setting_logo"}

    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        files=files,
        data=data,
    )
    assert response.status_code == 401


def test_upload_image_normal_user_forbidden(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    files = {"file": ("test.png", _png_content(), "image/png")}
    data = {"file_type": "image", "visibility": "public", "purpose": "system_setting_logo"}

    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=normal_user_token_headers,
        files=files,
        data=data,
    )
    assert response.status_code == 403


def test_upload_requires_matching_purpose_permission(client: TestClient, session: Session) -> None:
    permission = session.exec(select(Permission).where(Permission.resource == "system_setting", Permission.action == "upload_favicon")).first()
    assert permission is not None

    role = Role(name=f"favicon_uploader_{uuid.uuid4().hex[:8]}", description="Favicon uploader")
    user = User(
        email=f"favicon_uploader_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=get_password_hash("password1234"),
        is_active=True,
    )
    session.add(role)
    session.add(user)
    session.commit()
    session.refresh(role)
    session.refresh(user)
    session.add(RolePermission(role_id=role.id, permission_id=permission.id))
    session.add(UserRole(user_id=user.id, role_id=role.id))
    session.commit()

    headers = {"Authorization": f"Bearer {create_access_token(subject=user.id)}"}

    logo_response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=headers,
        files={"file": ("test.png", _png_content(), "image/png")},
        data={"file_type": "image", "visibility": "public", "purpose": "system_setting_logo"},
    )
    assert logo_response.status_code == 403

    favicon_response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=headers,
        files={"file": ("test.png", _png_content(), "image/png")},
        data={"file_type": "image", "visibility": "public", "purpose": "system_setting_favicon"},
    )
    assert_success(favicon_response, 201)


def test_upload_image_wrong_extension(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    files = {"file": ("test.txt", b"fake", "text/plain")}
    data = {"file_type": "image", "visibility": "public", "purpose": "system_setting_logo"}

    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=superuser_token_headers,
        files=files,
        data=data,
    )
    assert response.status_code == 400
    assert "Extension not allowed" in response.json()["message"]


def test_upload_image_wrong_signature(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    content = b"fake png data here that does not start with correct header"
    files = {"file": ("test.png", content, "image/png")}
    data = {"file_type": "image", "visibility": "public", "purpose": "system_setting_logo"}

    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=superuser_token_headers,
        files=files,
        data=data,
    )
    assert response.status_code == 400
    assert "Invalid image file signature for png" in response.json()["message"]


def test_upload_private_image(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    files = {"file": ("test.jpg", _jpg_content(), "image/jpeg")}
    data = {"file_type": "image", "visibility": "private", "purpose": "system_setting_logo"}

    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=superuser_token_headers,
        files=files,
        data=data,
    )
    assert response.status_code == 201
    resp = response.json()
    assert resp["code"] == 201
    assert resp["data"]["visibility"] == "private"
    assert resp["data"]["public_url"] is None


def test_upload_rejects_mime_type_that_does_not_match_extension(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    files = {"file": ("test.png", _png_content(), "image/jpeg")}
    data = {"file_type": "image", "visibility": "public", "purpose": "system_setting_logo"}

    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=superuser_token_headers,
        files=files,
        data=data,
    )
    assert response.status_code == 400
    assert response.json()["message"] == "Invalid MIME type for .png"


def test_upload_rejects_configured_but_unsupported_extension(client: TestClient, superuser_token_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "UPLOAD_ALLOWED_IMAGE_EXTENSIONS", "png,svg")
    files = {"file": ("test.svg", b"<svg></svg>", "image/svg+xml")}
    data = {"file_type": "image", "visibility": "public", "purpose": "system_setting_logo"}

    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=superuser_token_headers,
        files=files,
        data=data,
    )
    assert response.status_code == 400
    assert response.json()["message"] == "Unsupported image extension"


def test_upload_rejects_too_long_filename_before_saving(client: TestClient, superuser_token_headers: dict[str, str], tmp_path: Path) -> None:
    filename = f"{'a' * 252}.png"
    files = {"file": (filename, _png_content(), "image/png")}
    data = {"file_type": "image", "visibility": "public", "purpose": "system_setting_logo"}

    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=superuser_token_headers,
        files=files,
        data=data,
    )
    assert response.status_code == 400
    assert response.json()["message"] == "Filename too long. Max length is 255"
    assert _saved_files(tmp_path / "public") == []


def test_upload_rejects_too_long_purpose_before_saving(client: TestClient, superuser_token_headers: dict[str, str], tmp_path: Path) -> None:
    files = {"file": ("test.png", _png_content(), "image/png")}
    data = {"file_type": "image", "visibility": "public", "purpose": "x" * 101}

    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=superuser_token_headers,
        files=files,
        data=data,
    )
    assert response.status_code == 422
    assert _saved_files(tmp_path / "public") == []


def test_upload_requires_purpose(client: TestClient, superuser_token_headers: dict[str, str], tmp_path: Path) -> None:
    files = {"file": ("test.png", _png_content(), "image/png")}
    data = {"file_type": "image", "visibility": "public"}

    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=superuser_token_headers,
        files=files,
        data=data,
    )
    assert response.status_code == 422
    assert _saved_files(tmp_path / "public") == []


def test_upload_rejects_unknown_purpose(client: TestClient, superuser_token_headers: dict[str, str], tmp_path: Path) -> None:
    files = {"file": ("test.png", _png_content(), "image/png")}
    data = {"file_type": "image", "visibility": "public", "purpose": "unknown"}

    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=superuser_token_headers,
        files=files,
        data=data,
    )
    assert response.status_code == 422
    assert _saved_files(tmp_path / "public") == []


def test_upload_public_url_uses_configured_prefix(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "UPLOAD_PUBLIC_URL_PREFIX", "/assets/uploads")
    files = {"file": ("test.png", _png_content(), "image/png")}
    data = {"file_type": "image", "visibility": "public", "purpose": "system_setting_logo"}

    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=superuser_token_headers,
        files=files,
        data=data,
    )
    data = assert_success(response, 201)
    assert data["public_url"].startswith("/assets/uploads/")


def test_public_upload_mount_uses_configured_prefix(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "UPLOAD_PUBLIC_URL_PREFIX", "/assets/uploads")
    monkeypatch.setattr(settings, "UPLOAD_PUBLIC_DIR", str(tmp_path / "public_mount"))
    monkeypatch.setattr(settings, "UPLOAD_PRIVATE_DIR", str(tmp_path / "private_mount"))
    test_app = FastAPI()

    mount_public_uploads(test_app)

    assert any(route.path == "/assets/uploads" for route in test_app.routes)


def test_deleting_uploader_keeps_upload_record_and_clears_created_by(
    client: TestClient,
    session: Session,
    superuser_token_headers: dict[str, str],
) -> None:
    permission = session.exec(select(Permission).where(Permission.resource == "system_setting", Permission.action == "upload_logo")).first()
    assert permission is not None

    uploader_role = Role(name=f"uploader_{uuid.uuid4().hex[:8]}", description="Uploader")
    uploader = User(
        email=f"uploader_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=get_password_hash("password1234"),
        is_active=True,
    )
    session.add(uploader_role)
    session.add(uploader)
    session.commit()
    session.refresh(uploader_role)
    session.refresh(uploader)
    session.add(RolePermission(role_id=uploader_role.id, permission_id=permission.id))
    session.add(UserRole(user_id=uploader.id, role_id=uploader_role.id))
    session.commit()

    uploader_headers = {"Authorization": f"Bearer {create_access_token(subject=uploader.id)}"}
    files = {"file": ("test.png", _png_content(), "image/png")}
    upload_response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=uploader_headers,
        files=files,
        data={"file_type": "image", "visibility": "public", "purpose": "system_setting_logo"},
    )
    upload_data = assert_success(upload_response, 201)

    delete_response = client.delete(
        f"{settings.API_V1_STR}/admin/users/{uploader.id}",
        headers=superuser_token_headers,
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["code"] == 200

    session.expire_all()
    upload_record = session.get(UploadFile, upload_data["id"])
    assert upload_record is not None
    assert upload_record.created_by_id is None
