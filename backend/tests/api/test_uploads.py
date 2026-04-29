from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings

def test_upload_image_success(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    image_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 10
    files = {"file": ("test.png", image_content, "image/png")}
    data = {"file_type": "image", "visibility": "public"}
    
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
    image_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 10
    files = {"file": ("test.png", image_content, "image/png")}
    data = {"file_type": "image", "visibility": "public"}
    
    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        files=files,
        data=data,
    )
    assert response.status_code == 401


def test_upload_image_normal_user_forbidden(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    image_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 10
    files = {"file": ("test.png", image_content, "image/png")}
    data = {"file_type": "image", "visibility": "public"}
    
    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=normal_user_token_headers,
        files=files,
        data=data,
    )
    assert response.status_code == 403


def test_upload_image_wrong_extension(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    content = b"fake"
    files = {"file": ("test.txt", content, "text/plain")}
    data = {"file_type": "image", "visibility": "public"}
    
    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=superuser_token_headers,
        files=files,
        data=data,
    )
    assert response.status_code == 400
    assert "Extension not allowed" in response.json()["message"]


def test_upload_image_wrong_signature(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    content = b"fake png data here that does not start with correct header"
    files = {"file": ("test.png", content, "image/png")}
    data = {"file_type": "image", "visibility": "public"}
    
    response = client.post(
        f"{settings.API_V1_STR}/uploads",
        headers=superuser_token_headers,
        files=files,
        data=data,
    )
    assert response.status_code == 400
    assert "Invalid image file signature for png" in response.json()["message"]


def test_upload_private_image(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    image_content = b"\xff\xd8\xff" + b"\x00" * 10
    files = {"file": ("test.jpg", image_content, "image/jpeg")}
    data = {"file_type": "image", "visibility": "private"}
    
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
