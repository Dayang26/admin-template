
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models.db import Class, Role, User, UserRole
from tests.conftest import assert_error, assert_success


def test_teacher_get_classes_success(client: TestClient, normal_user_token_headers: dict[str, str], session: Session) -> None:
    # 1. 准备数据：normal_user (teacher) 属于两个班级
    user = session.exec(select(User).where(User.email == "normal@example.com")).first()

    role_teacher = session.exec(select(Role).where(Role.name == "teacher")).first()

    c1 = Class(name="Teacher Class 1")
    c2 = Class(name="Teacher Class 2")
    c3 = Class(name="Other Class")
    session.add_all([c1, c2, c3])
    session.commit()
    session.refresh(c1)
    session.refresh(c2)
    session.refresh(c3)

    session.add(UserRole(user_id=user.id, role_id=role_teacher.id, class_id=c1.id))
    session.add(UserRole(user_id=user.id, role_id=role_teacher.id, class_id=c2.id))
    session.commit()

    # 2. 调用接口
    response = client.get(f"{settings.API_V1_STR}/teacher/classes", headers=normal_user_token_headers)
    data = assert_success(response)
    assert len(data) == 2
    assert any(c["name"] == "Teacher Class 1" for c in data)
    assert all(c["name"] != "Other Class" for c in data)


def test_teacher_get_class_members_success(client: TestClient, normal_user_token_headers: dict[str, str], session: Session) -> None:
    # 1. 准备数据
    user = session.exec(select(User).where(User.email == "normal@example.com")).first()
    role_teacher = session.exec(select(Role).where(Role.name == "teacher")).first()
    role_student = session.exec(select(Role).where(Role.name == "student")).first()
    if not role_student:
        role_student = Role(name="student", description="Student")
        session.add(role_student)
        session.commit()
        session.refresh(role_student)

    c1 = Class(name="Member Test Class")
    session.add(c1)
    session.commit()
    session.refresh(c1)

    # 教师入班
    session.add(UserRole(user_id=user.id, role_id=role_teacher.id, class_id=c1.id))
    # 学生入班
    s1 = User(email="student1@example.com", hashed_password="pw")
    session.add(s1)
    session.commit()
    session.refresh(s1)
    session.add(UserRole(user_id=s1.id, role_id=role_student.id, class_id=c1.id))
    session.commit()

    # 2. 调用接口
    response = client.get(f"{settings.API_V1_STR}/teacher/classes/{c1.id}/members", headers=normal_user_token_headers)
    data = assert_success(response)
    assert data["total"] == 2  # 教师自己 + 学生
    assert any(m["email"] == "student1@example.com" for m in data["items"])


def test_teacher_get_class_members_forbidden(client: TestClient, normal_user_token_headers: dict[str, str], session: Session) -> None:
    # 尝试访问不属于自己的班级
    c_other = Class(name="Not My Class")
    session.add(c_other)
    session.commit()
    session.refresh(c_other)

    response = client.get(f"{settings.API_V1_STR}/teacher/classes/{c_other.id}/members", headers=normal_user_token_headers)
    assert_error(response, 403, "You are not a member of this class")


def test_teacher_get_classes_empty(client: TestClient, session: Session) -> None:
    """Test teacher with no classes but has teacher role (class:read permission)."""
    from app.core.security import create_access_token

    user = User(email="no_classes@example.com", hashed_password="pw")
    session.add(user)
    session.commit()
    session.refresh(user)

    # 分配 teacher 角色（有 class:read 权限）
    teacher_role = session.exec(select(Role).where(Role.name == "teacher")).first()
    session.add(UserRole(user_id=user.id, role_id=teacher_role.id, class_id=None))
    session.commit()

    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"{settings.API_V1_STR}/teacher/classes", headers=headers)
    data = assert_success(response)
    assert len(data) == 0


def test_teacher_get_class_members_empty_class(client: TestClient, normal_user_token_headers: dict[str, str], session: Session) -> None:
    """Test getting members for a class that only has the teacher themselves."""
    user = session.exec(select(User).where(User.email == "normal@example.com")).first()
    role_teacher = session.exec(select(Role).where(Role.name == "teacher")).first()

    c1 = Class(name="Teacher Only Class")
    session.add(c1)
    session.commit()
    session.refresh(c1)

    session.add(UserRole(user_id=user.id, role_id=role_teacher.id, class_id=c1.id))
    session.commit()

    response = client.get(f"{settings.API_V1_STR}/teacher/classes/{c1.id}/members", headers=normal_user_token_headers)
    data = assert_success(response)
    assert data["total"] == 1
    assert data["items"][0]["email"] == "normal@example.com"
