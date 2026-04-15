import time

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models.db import Role, User
from app.schemas import UserPublic


#### get_users #### start
def test_get_users_superuser(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    """
    Test that a superuser can retrieve the paginated list of users,
    verifying content and sorting.
    """
    # 创建一个用户，等待片刻，再创建另一个，以测试按创建时间降序排列
    user_2 = User(email="user2@example.com", hashed_password="password2")
    session.add(user_2)
    session.commit()
    time.sleep(0.1)
    user_3 = User(email="user3@example.com", hashed_password="password3")
    session.add(user_3)
    session.commit()

    response = client.get(
        f"{settings.API_V1_STR}/admin/users/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200

    content = response.json()
    assert "items" in content
    assert "total" in content
    assert "page" in content
    assert "size" in content
    assert "pages" in content
    assert isinstance(content["items"], list)

    # 总数应包括超级用户和我们刚刚创建的2个用户
    assert content["total"] >= 3

    items = content["items"]
    # 列表中的第一项应该是最新创建的用户 (user_3)
    assert items[0]["email"] == user_3.email

    # 验证返回的数据符合 UserPublic 结构
    # 并且不包含密码等敏感信息
    for item in items:
        UserPublic.model_validate(item)
        assert "password" not in item
        assert "hashed_password" not in item


def test_get_users_pagination(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    """Test pagination of the users list."""
    # 创建6个用户用于分页测试
    for i in range(6):
        user = User(email=f"pageuser{i}@example.com", hashed_password="password")
        session.add(user)
    session.commit()

    # 获取第1页，每页5条
    response_page1 = client.get(f"{settings.API_V1_STR}/admin/users/?page=1&size=5", headers=superuser_token_headers)
    assert response_page1.status_code == 200
    content_page1 = response_page1.json()
    assert content_page1["page"] == 1
    assert content_page1["size"] == 5
    assert len(content_page1["items"]) == 5
    assert content_page1["total"] >= 6

    # 获取第2页，每页5条
    response_page2 = client.get(f"{settings.API_V1_STR}/admin/users/?page=2&size=5", headers=superuser_token_headers)
    assert response_page2.status_code == 200
    content_page2 = response_page2.json()
    assert content_page2["page"] == 2
    assert len(content_page2["items"]) >= 1  # 第二页至少有1个用户


def test_get_users_normal_user_forbidden(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    """
    Test that a normal user gets a 403 Forbidden error when trying to access the superuser endpoint.
    """
    response = client.get(
        f"{settings.API_V1_STR}/admin/users/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "The user doesn't have enough privileges"


def test_get_users_unauthorized(client: TestClient) -> None:
    """
    Test that accessing the endpoint without any authentication token returns 401 Unauthorized.
    """
    response = client.get(f"{settings.API_V1_STR}/admin/users/")
    assert response.status_code == 401


def test_create_user_by_admin_success(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    role = Role(name="test_role", description="Test Role")
    session.add(role)
    session.commit()

    payload = {"email": "newuser@example.com", "password": "securepassword", "full_name": "New User", "is_active": True, "roles": ["test_role"]}
    response = client.post(f"{settings.API_V1_STR}/admin/users/", headers=superuser_token_headers, json=payload)
    assert response.status_code == 201
    content = response.json()
    assert content["email"] == "newuser@example.com"
    assert "id" in content
    assert "password" not in content


#### get_users #### end


#### create_user_by_admin #### start
def test_create_user_by_admin_existing_email(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    role = Role(name="test_role2", description="Test Role")
    session.add(role)
    user = User(email="existing@example.com", hashed_password="password")
    session.add(user)
    session.commit()

    payload = {
        "email": "existing@example.com",
        "password": "securepassword",
        "roles": ["test_role2"]
    }
    response = client.post(
        f"{settings.API_V1_STR}/admin/users/",
        headers=superuser_token_headers,
        json=payload
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "A user with this email already exists"


def test_create_user_by_admin_missing_role(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    payload = {"email": "newuser2@example.com", "password": "securepassword", "roles": ["non_existent_role"]}
    response = client.post(f"{settings.API_V1_STR}/admin/users/", headers=superuser_token_headers, json=payload)
    assert response.status_code == 400
    assert "Role(s) not found:" in response.json()["detail"]


def test_create_user_by_admin_assign_superuser(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    # superuser role already exists from init_db, no need to create it

    payload = {"email": "newuser3@example.com", "password": "securepassword", "roles": ["superuser"]}
    response = client.post(f"{settings.API_V1_STR}/admin/users/", headers=superuser_token_headers, json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot assign the 'superuser' role"


def test_create_user_by_admin_normal_user_forbidden(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    payload = {"email": "newuser4@example.com", "password": "securepassword", "roles": ["test_role"]}
    response = client.post(f"{settings.API_V1_STR}/admin/users/", headers=normal_user_token_headers, json=payload)
    assert response.status_code == 403


def test_create_user_by_admin_unauthorized(client: TestClient) -> None:
    payload = {"email": "newuser5@example.com", "password": "securepassword", "roles": ["test_role"]}
    response = client.post(f"{settings.API_V1_STR}/admin/users/", json=payload)
    assert response.status_code == 401


#### create_user_by_admin #### end


#### update_user_by_admin #### start
def test_update_user_by_admin_success(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    """Test updating a normal user's basic information (success)."""
    # Create a test user
    user = User(email="update_test@example.com", hashed_password="oldpassword", full_name="Old Name", is_active=True)
    session.add(user)
    session.commit()
    session.refresh(user)

    # Update user
    payload = {"full_name": "Updated Name", "is_active": False}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{user.id}",
        headers=superuser_token_headers,
        json=payload
    )
    assert response.status_code == 200
    content = response.json()
    assert content["full_name"] == "Updated Name"
    assert content["is_active"] is False
    assert content["email"] == "update_test@example.com"


def test_update_user_by_admin_password(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    """Test updating a user's password."""
    from sqlmodel import select

    # Create a test user
    user = User(email="update_password@example.com", hashed_password="oldpassword", full_name="Test User")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Update password
    payload = {"password": "newsecurepassword"}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{user.id}",
        headers=superuser_token_headers,
        json=payload
    )
    assert response.status_code == 200

    # Verify password was updated
    session.refresh(user)
    from app.core.security import verify_password
    assert verify_password("newsecurepassword", user.hashed_password)


def test_update_user_by_admin_replace_roles(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    """Test role replacement logic - old roles should be removed and new roles assigned."""
    from sqlmodel import select
    from app.models.db import UserRole

    # Create test roles
    role_teacher = Role(name="role_teacher", description="Teacher Role")
    session.add(role_teacher)
    role_student = Role(name="role_student", description="Student Role")
    session.add(role_student)
    session.commit()
    session.refresh(role_teacher)
    session.refresh(role_student)

    # Create a test user with teacher role
    user = User(email="role_replace@example.com", hashed_password="password")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Assign teacher role
    user_role = UserRole(user_id=user.id, role_id=role_teacher.id, class_id=None)
    session.add(user_role)
    session.commit()

    # Replace roles: remove teacher, add student
    payload = {"roles": ["role_student"]}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{user.id}",
        headers=superuser_token_headers,
        json=payload
    )
    assert response.status_code == 200

    # Verify old role is removed and new role is added
    statement = select(UserRole).where(UserRole.user_id == user.id)
    user_roles = session.exec(statement).all()
    role_ids = [ur.role_id for ur in user_roles]
    assert role_student.id in role_ids
    assert role_teacher.id not in role_ids


def test_update_user_by_admin_superuser_forbidden(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    """Test that a superuser cannot modify another superuser's information."""
    from sqlmodel import select
    from app.models.db import UserRole

    # superuser role already exists from init_db
    role_superuser = session.exec(select(Role).where(Role.name == "superuser")).first()

    # Create another superuser (target)
    target_user = User(email="target_superuser@example.com", hashed_password="password", is_active=True)
    session.add(target_user)
    session.commit()
    session.refresh(target_user)

    # Assign superuser role to target
    user_role = UserRole(user_id=target_user.id, role_id=role_superuser.id, class_id=None)
    session.add(user_role)
    session.commit()

    # Try to modify the other superuser
    payload = {"full_name": "Hacked Name"}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{target_user.id}",
        headers=superuser_token_headers,
        json=payload
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot modify information of other superusers"


def test_update_user_by_admin_self_allowed(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    """Test that a superuser can modify their own information."""
    from sqlmodel import select

    # Get superuser role
    role_superuser = session.exec(select(Role).where(Role.name == "superuser")).first()

    # Get the current superuser (from headers)
    from app.core.security import create_access_token
    import jwt
    from app.core.config import settings

    # Decode token to get user id
    token = superuser_token_headers["Authorization"].replace("Bearer ", "")
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    from app.models.db import User
    current_user = session.get(User, payload["sub"])

    # Update own information
    payload = {"full_name": "My Updated Name"}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{current_user.id}",
        headers=superuser_token_headers,
        json=payload
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "My Updated Name"


def test_update_user_by_admin_assign_superuser_forbidden(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    """Test that assigning superuser role is forbidden."""

    # Create a test user
    user = User(email="assign_superuser@example.com", hashed_password="password")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Try to assign superuser role
    payload = {"roles": ["superuser"]}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{user.id}",
        headers=superuser_token_headers,
        json=payload
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot assign the 'superuser' role"


def test_update_user_by_admin_not_found(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """Test updating a non-existent user returns 404."""
    import uuid
    fake_id = uuid.uuid4()
    payload = {"full_name": "Test"}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{fake_id}",
        headers=superuser_token_headers,
        json=payload
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user_by_admin_missing_role(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    """Test updating user with non-existent role returns 400."""
    from sqlmodel import select

    # Create a test user
    user = User(email="missing_role@example.com", hashed_password="password")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Try to assign non-existent role
    payload = {"roles": ["non_existent_role_xyz"]}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{user.id}",
        headers=superuser_token_headers,
        json=payload
    )
    assert response.status_code == 400
    assert "Role(s) not found:" in response.json()["detail"]


def test_update_user_by_admin_normal_user_forbidden(client: TestClient, normal_user_token_headers: dict[str, str], session: Session) -> None:
    """Test that a normal user gets 403 Forbidden."""
    user = User(email="normal_forbidden@example.com", hashed_password="password")
    session.add(user)
    session.commit()
    session.refresh(user)

    payload = {"full_name": "Hacker"}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{user.id}",
        headers=normal_user_token_headers,
        json=payload
    )
    assert response.status_code == 403


def test_update_user_by_admin_unauthorized(client: TestClient) -> None:
    """Test that unauthorized access returns 401."""
    import uuid
    fake_id = uuid.uuid4()
    payload = {"full_name": "Hacker"}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{fake_id}",
        json=payload
    )
    assert response.status_code == 401


def test_update_user_by_admin_partial_update(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    """Test partial update (only one field updated, others remain unchanged)."""
    user = User(
        email="partial_update@example.com",
        hashed_password="password123",
        full_name="Original Name",
        is_active=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Only updating is_active
    payload = {"is_active": True}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/users/{user.id}",
        headers=superuser_token_headers,
        json=payload
    )
    assert response.status_code == 200
    content = response.json()
    assert content["is_active"] is True
    assert content["full_name"] == "Original Name"


#### update_user_by_admin #### end