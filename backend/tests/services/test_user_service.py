import uuid
from pathlib import Path

import pytest
from sqlmodel import Session

from app.core.config import settings
from app.core.security import verify_password
from app.models.db import UploadFile, User
from app.schemas.user import UserCreateReq
from app.services.user_service import create_user, delete_user


def test_create_user(session: Session) -> None:
    """Test create_user logic (without roles)."""
    user_in = UserCreateReq(email="simple_create@example.com", password="testpassword", full_name="Simple Create")
    user = create_user(session=session, user_create=user_in)

    assert user.email == "simple_create@example.com"
    assert user.full_name == "Simple Create"
    assert user.hashed_password is not None

    is_correct, _ = verify_password("testpassword", user.hashed_password)
    assert is_correct


def test_delete_user_with_roles(session: Session) -> None:
    """Test delete_user logic when the user has roles assigned."""
    from app.models.db import Role, UserRole

    role = Role(name="test_delete_role")
    session.add(role)

    user = User(email="with_roles@example.com", hashed_password="pw")
    session.add(user)
    session.commit()
    session.refresh(role)
    session.refresh(user)

    session.add(UserRole(user_id=user.id, role_id=role.id))
    session.commit()

    target_id = user.id
    current_user_id = uuid.uuid4()  # some other user doing the deletion

    # Try to delete
    delete_user(session=session, target_user_id=target_id, current_user_id=current_user_id)

    # Verify deletion
    deleted_user = session.get(User, target_id)
    assert deleted_user is None


def test_delete_user_cleans_avatar_upload(session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "UPLOAD_PUBLIC_DIR", str(tmp_path / "public"))
    monkeypatch.setattr(settings, "UPLOAD_PRIVATE_DIR", str(tmp_path / "private"))

    user = User(email="with_avatar@example.com", hashed_password="pw")
    session.add(user)
    session.commit()
    session.refresh(user)

    storage_key = "2026/05/avatar.png"
    avatar_path = tmp_path / "public" / storage_key
    avatar_path.parent.mkdir(parents=True)
    avatar_path.write_bytes(b"\x89PNG\r\n\x1a\n")

    upload_file = UploadFile(
        original_filename="avatar.png",
        stored_filename="avatar.png",
        extension="png",
        content_type="image/png",
        size_bytes=8,
        sha256="0" * 64,
        file_type="image",
        visibility="public",
        storage_provider="local",
        storage_key=storage_key,
        public_url=f"/uploads/public/{storage_key}",
        purpose="user_avatar",
        created_by_id=user.id,
    )
    session.add(upload_file)
    session.commit()
    session.refresh(upload_file)

    user.avatar_file_id = upload_file.id
    session.add(user)
    session.commit()

    delete_user(session=session, target_user_id=user.id, current_user_id=uuid.uuid4())

    assert session.get(User, user.id) is None
    assert session.get(UploadFile, upload_file.id) is None
    assert not avatar_path.exists()
