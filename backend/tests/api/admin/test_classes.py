import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models.db import Class, Role, User, UserRole
from tests.conftest import assert_error, assert_success


def test_get_classes_success(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    class1 = Class(name="Class A", description="Desc A")
    class2 = Class(name="Class B", description="Desc B")
    session.add(class1)
    session.add(class2)
    session.commit()

    response = client.get(
        f"{settings.API_V1_STR}/admin/classes/",
        headers=superuser_token_headers,
    )
    data = assert_success(response)
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 2


def test_get_classes_search(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    class1 = Class(name="Math 101", description="Math")
    class2 = Class(name="History 101", description="History")
    session.add(class1)
    session.add(class2)
    session.commit()

    response = client.get(
        f"{settings.API_V1_STR}/admin/classes/?name=Math",
        headers=superuser_token_headers,
    )
    data = assert_success(response)
    assert "items" in data
    assert len(data["items"]) >= 1
    assert any(item["name"] == "Math 101" for item in data["items"])
    assert all("History" not in item["name"] for item in data["items"])


def test_get_classes_pagination(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    for _ in range(6):
        session.add(Class(name=f"Page Class {uuid.uuid4()}"))
    session.commit()

    response = client.get(
        f"{settings.API_V1_STR}/admin/classes/?page=1&size=5",
        headers=superuser_token_headers,
    )
    data = assert_success(response)
    assert data["size"] == 5
    assert len(data["items"]) == 5

    response2 = client.get(
        f"{settings.API_V1_STR}/admin/classes/?page=2&size=5",
        headers=superuser_token_headers,
    )
    data2 = assert_success(response2)
    assert data2["page"] == 2
    assert len(data2["items"]) >= 1


def test_get_classes_forbidden(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/admin/classes/",
        headers=normal_user_token_headers,
    )
    # teacher 角色有 class:read 权限，可以访问班级列表
    assert response.status_code == 200


def test_get_classes_unauthorized(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/admin/classes/")
    assert_error(response, 401)


def test_create_class_success(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    payload = {"name": f"New Class {uuid.uuid4()}", "description": "New Desc"}
    response = client.post(
        f"{settings.API_V1_STR}/admin/classes/",
        headers=superuser_token_headers,
        json=payload,
    )
    data = assert_success(response, 201)
    assert data["name"] == payload["name"]
    assert data["description"] == "New Desc"
    assert "id" in data


def test_create_class_name_exists(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    name = f"Duplicate Class {uuid.uuid4()}"
    class_db = Class(name=name)
    session.add(class_db)
    session.commit()

    payload = {"name": name}
    response = client.post(
        f"{settings.API_V1_STR}/admin/classes/",
        headers=superuser_token_headers,
        json=payload,
    )
    assert_error(response, 400, "The class name already exists in the system.")


def test_create_class_forbidden(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    payload = {"name": "New Class Forbidden"}
    response = client.post(
        f"{settings.API_V1_STR}/admin/classes/",
        headers=normal_user_token_headers,
        json=payload,
    )
    assert_error(response, 403)


def test_create_class_unauthorized(client: TestClient) -> None:
    payload = {"name": "New Class Unauth"}
    response = client.post(
        f"{settings.API_V1_STR}/admin/classes/",
        json=payload,
    )
    assert_error(response, 401)


def test_get_class_success(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    db_class = Class(name=f"Test Get Class {uuid.uuid4()}")
    session.add(db_class)
    session.commit()
    session.refresh(db_class)

    response = client.get(
        f"{settings.API_V1_STR}/admin/classes/{db_class.id}",
        headers=superuser_token_headers,
    )
    data = assert_success(response)
    assert data["id"] == str(db_class.id)
    assert data["name"] == db_class.name


def test_get_class_not_found(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    fake_id = uuid.uuid4()
    response = client.get(
        f"{settings.API_V1_STR}/admin/classes/{fake_id}",
        headers=superuser_token_headers,
    )
    assert_error(response, 404, "Class not found.")


def test_get_class_forbidden(client: TestClient, normal_user_token_headers: dict[str, str], session: Session) -> None:
    db_class = Class(name=f"Test Class {uuid.uuid4()}")
    session.add(db_class)
    session.commit()
    session.refresh(db_class)

    response = client.get(
        f"{settings.API_V1_STR}/admin/classes/{db_class.id}",
        headers=normal_user_token_headers,
    )
    # teacher 角色有 class:read 权限
    assert response.status_code == 200


def test_get_class_unauthorized(client: TestClient) -> None:
    fake_id = uuid.uuid4()
    response = client.get(f"{settings.API_V1_STR}/admin/classes/{fake_id}")
    assert_error(response, 401)


def test_update_class_success(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    db_class = Class(name=f"Old Name {uuid.uuid4()}", description="Old Desc")
    session.add(db_class)
    session.commit()
    session.refresh(db_class)

    new_name = f"New Name {uuid.uuid4()}"
    payload = {"name": new_name, "description": "New Desc"}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/classes/{db_class.id}",
        headers=superuser_token_headers,
        json=payload,
    )
    data = assert_success(response)
    assert data["name"] == new_name
    assert data["description"] == "New Desc"


def test_update_class_partial(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    db_class = Class(name=f"Old Name {uuid.uuid4()}", description="Old Desc")
    session.add(db_class)
    session.commit()
    session.refresh(db_class)

    new_name = f"New Name {uuid.uuid4()}"
    payload = {"name": new_name}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/classes/{db_class.id}",
        headers=superuser_token_headers,
        json=payload,
    )
    data = assert_success(response)
    assert data["name"] == new_name
    assert data["description"] == "Old Desc"


def test_update_class_name_exists(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    name1 = f"Name 1 {uuid.uuid4()}"
    name2 = f"Name 2 {uuid.uuid4()}"
    class1 = Class(name=name1)
    class2 = Class(name=name2)
    session.add(class1)
    session.add(class2)
    session.commit()
    session.refresh(class1)

    payload = {"name": name2}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/classes/{class1.id}",
        headers=superuser_token_headers,
        json=payload,
    )
    assert_error(response, 400, "The class name already exists in the system.")


def test_update_class_not_found(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    fake_id = uuid.uuid4()
    payload = {"name": "New Name"}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/classes/{fake_id}",
        headers=superuser_token_headers,
        json=payload,
    )
    assert_error(response, 404, "Class not found.")


def test_update_class_forbidden(client: TestClient, normal_user_token_headers: dict[str, str], session: Session) -> None:
    db_class = Class(name=f"Test Class {uuid.uuid4()}")
    session.add(db_class)
    session.commit()
    session.refresh(db_class)

    payload = {"name": "New Name"}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/classes/{db_class.id}",
        headers=normal_user_token_headers,
        json=payload,
    )
    assert_error(response, 403)


def test_update_class_unauthorized(client: TestClient) -> None:
    fake_id = uuid.uuid4()
    payload = {"name": "New Name"}
    response = client.patch(
        f"{settings.API_V1_STR}/admin/classes/{fake_id}",
        json=payload,
    )
    assert_error(response, 401)


def test_delete_class_success(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    db_class = Class(name=f"To Delete {uuid.uuid4()}")
    session.add(db_class)
    session.commit()
    session.refresh(db_class)

    response = client.delete(
        f"{settings.API_V1_STR}/admin/classes/{db_class.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"] is None

    db_class_after = session.get(Class, db_class.id)
    assert db_class_after is None


def test_delete_class_has_users(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    db_class = Class(name=f"To Delete Has Users {uuid.uuid4()}")
    session.add(db_class)
    role = Role(name=f"role_{uuid.uuid4()}")
    session.add(role)
    user = User(email=f"user_{uuid.uuid4()}@example.com", hashed_password="pw")
    session.add(user)
    session.commit()
    session.refresh(db_class)
    session.refresh(role)
    session.refresh(user)

    user_role = UserRole(user_id=user.id, role_id=role.id, class_id=db_class.id)
    session.add(user_role)
    session.commit()

    response = client.delete(
        f"{settings.API_V1_STR}/admin/classes/{db_class.id}",
        headers=superuser_token_headers,
    )
    assert_error(response, 400, "该班级下存在关联用户角色，无法删除")


def test_delete_class_not_found(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    fake_id = uuid.uuid4()
    response = client.delete(
        f"{settings.API_V1_STR}/admin/classes/{fake_id}",
        headers=superuser_token_headers,
    )
    assert_error(response, 404, "Class not found.")


def test_delete_class_forbidden(client: TestClient, normal_user_token_headers: dict[str, str], session: Session) -> None:
    db_class = Class(name=f"Test Class {uuid.uuid4()}")
    session.add(db_class)
    session.commit()
    session.refresh(db_class)

    response = client.delete(
        f"{settings.API_V1_STR}/admin/classes/{db_class.id}",
        headers=normal_user_token_headers,
    )
    assert_error(response, 403)


def test_delete_class_unauthorized(client: TestClient) -> None:
    fake_id = uuid.uuid4()
    response = client.delete(f"{settings.API_V1_STR}/admin/classes/{fake_id}")
    assert_error(response, 401)


#### class_members #### start


def test_add_class_member_success(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    # 1. 创建班级、角色、用户
    db_class = Class(name=f"Class Member Test {uuid.uuid4()}")
    session.add(db_class)
    db_role = Role(name=f"role_member_{uuid.uuid4()}")
    session.add(db_role)
    db_user = User(email=f"member_{uuid.uuid4()}@example.com", hashed_password="pw")
    session.add(db_user)
    session.commit()
    session.refresh(db_class)
    session.refresh(db_role)
    session.refresh(db_user)

    # 2. 调用接口添加成员
    payload = {"user_id": str(db_user.id), "role": db_role.name}
    response = client.post(
        f"{settings.API_V1_STR}/admin/classes/{db_class.id}/members",
        headers=superuser_token_headers,
        json=payload,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "成员已添加"

    # 3. 验证数据库
    statement = select(UserRole).where(UserRole.class_id == db_class.id, UserRole.user_id == db_user.id)
    ur = session.exec(statement).first()
    assert ur is not None
    assert ur.role_id == db_role.id


def test_get_class_members_success(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    # 1. 创建班级、角色、用户并关联
    db_class = Class(name=f"Class List Test {uuid.uuid4()}")
    session.add(db_class)
    db_role = Role(name=f"role_list_{uuid.uuid4()}")
    session.add(db_role)
    db_user = User(email=f"list_member_{uuid.uuid4()}@example.com", hashed_password="pw", full_name="List Member")
    session.add(db_user)
    session.commit()
    session.refresh(db_class)
    session.refresh(db_role)
    session.refresh(db_user)

    session.add(UserRole(user_id=db_user.id, role_id=db_role.id, class_id=db_class.id))
    session.commit()

    # 2. 调用接口获取列表
    response = client.get(f"{settings.API_V1_STR}/admin/classes/{db_class.id}/members", headers=superuser_token_headers)
    data = assert_success(response)
    assert data["total"] == 1
    assert data["items"][0]["user_id"] == str(db_user.id)
    assert data["items"][0]["email"] == db_user.email
    assert data["items"][0]["role"] == db_role.name


def test_remove_class_member_success(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    # 1. 创建班级、角色、用户并关联
    db_class = Class(name=f"Class Remove Test {uuid.uuid4()}")
    session.add(db_class)
    db_role = Role(name=f"role_remove_{uuid.uuid4()}")
    session.add(db_role)
    db_user = User(email=f"remove_member_{uuid.uuid4()}@example.com", hashed_password="pw")
    session.add(db_user)
    session.commit()
    session.refresh(db_class)
    session.refresh(db_role)
    session.refresh(db_user)

    session.add(UserRole(user_id=db_user.id, role_id=db_role.id, class_id=db_class.id))
    session.commit()

    # 2. 调用接口移除成员
    response = client.delete(
        f"{settings.API_V1_STR}/admin/classes/{db_class.id}/members/{db_user.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "成员已移除"

    # 3. 验证数据库
    session.expire_all()
    statement = select(UserRole).where(UserRole.class_id == db_class.id, UserRole.user_id == db_user.id)
    assert session.exec(statement).first() is None


def test_add_class_member_duplicate(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    """Test adding a member who already exists in the class with the same role."""
    db_class = Class(name=f"Duplicate Test {uuid.uuid4()}")
    db_role = Role(name=f"role_dup_{uuid.uuid4()}")
    db_user = User(email=f"dup_{uuid.uuid4()}@example.com", hashed_password="pw")
    session.add_all([db_class, db_role, db_user])
    session.commit()
    session.refresh(db_class)
    session.refresh(db_role)
    session.refresh(db_user)

    # First add
    payload = {"user_id": str(db_user.id), "role": db_role.name}
    client.post(f"{settings.API_V1_STR}/admin/classes/{db_class.id}/members", headers=superuser_token_headers, json=payload)

    # Second add (duplicate)
    response = client.post(f"{settings.API_V1_STR}/admin/classes/{db_class.id}/members", headers=superuser_token_headers, json=payload)
    assert_error(response, 400, "User already has this role in the class")


def test_add_class_member_invalid_resources(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    """Test adding member with non-existent class, user or role."""
    db_class = Class(name=f"Resource Test {uuid.uuid4()}")
    db_user = User(email=f"res_{uuid.uuid4()}@example.com", hashed_password="pw")
    session.add_all([db_class, db_user])
    session.commit()
    session.refresh(db_class)
    session.refresh(db_user)

    # 1. Invalid Class ID
    fake_class_id = uuid.uuid4()
    payload = {"user_id": str(db_user.id), "role": "teacher"}
    response = client.post(f"{settings.API_V1_STR}/admin/classes/{fake_class_id}/members", headers=superuser_token_headers, json=payload)
    assert_error(response, 404, "Class not found")

    # 2. Invalid User ID
    fake_user_id = uuid.uuid4()
    payload = {"user_id": str(fake_user_id), "role": "teacher"}
    response = client.post(f"{settings.API_V1_STR}/admin/classes/{db_class.id}/members", headers=superuser_token_headers, json=payload)
    assert_error(response, 404, "User not found")

    # 3. Invalid Role Name
    payload = {"user_id": str(db_user.id), "role": "non_existent_role"}
    response = client.post(f"{settings.API_V1_STR}/admin/classes/{db_class.id}/members", headers=superuser_token_headers, json=payload)
    assert_error(response, 400, "Role 'non_existent_role' not found")


def test_get_class_members_empty(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    """Test getting members for an empty class."""
    db_class = Class(name=f"Empty Class {uuid.uuid4()}")
    session.add(db_class)
    session.commit()
    session.refresh(db_class)

    response = client.get(f"{settings.API_V1_STR}/admin/classes/{db_class.id}/members", headers=superuser_token_headers)
    data = assert_success(response)
    assert data["total"] == 0
    assert len(data["items"]) == 0


def test_remove_class_member_not_found(client: TestClient, superuser_token_headers: dict[str, str], session: Session) -> None:
    """Test removing a member who is not in the class."""
    db_class = Class(name=f"Remove Not Found {uuid.uuid4()}")
    db_user = User(email=f"not_in_class_{uuid.uuid4()}@example.com", hashed_password="pw")
    session.add_all([db_class, db_user])
    session.commit()
    session.refresh(db_class)
    session.refresh(db_user)

    response = client.delete(f"{settings.API_V1_STR}/admin/classes/{db_class.id}/members/{db_user.id}", headers=superuser_token_headers)
    assert_error(response, 404, "Member not found in this class")


#### class_members #### end
