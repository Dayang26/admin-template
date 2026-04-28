import uuid

from sqlmodel import Session

from app.core.security import verify_password
from app.models.db import User
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
