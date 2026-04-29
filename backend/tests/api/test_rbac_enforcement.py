"""RBAC 权限校验全局推广测试。

验证 require_permission 真正根据数据库中的权限数据起效，
而不仅仅是验证超级管理员角色。
"""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models.db import Permission, Role, RolePermission, User, UserRole
from tests.conftest import assert_error


def _create_user_with_custom_role(
    session: Session,
    email: str,
    role_name: str,
    permissions: list[tuple[str, str]],
) -> dict[str, str]:
    """创建一个拥有自定义角色和指定权限的用户，返回 token headers。"""
    # 创建或获取角色
    role = session.exec(select(Role).where(Role.name == role_name)).first()
    if not role:
        role = Role(name=role_name, description=f"Test role: {role_name}")
        session.add(role)
        session.commit()
        session.refresh(role)

    # 绑定权限
    for resource, action in permissions:
        perm = session.exec(select(Permission).where(Permission.resource == resource, Permission.action == action)).first()
        if perm:
            existing = session.exec(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == perm.id,
                )
            ).first()
            if not existing:
                session.add(RolePermission(role_id=role.id, permission_id=perm.id))
    session.commit()

    # 创建用户
    user = User(email=email, hashed_password=get_password_hash("testpassword123"), is_active=True)
    session.add(user)
    session.commit()
    session.refresh(user)

    # 分配角色
    session.add(UserRole(user_id=user.id, role_id=role.id))
    session.commit()

    token = create_access_token(subject=user.id)
    return {"Authorization": f"Bearer {token}"}


class TestRBACUserModule:
    """用户管理模块 RBAC 测试。"""

    def test_user_with_read_permission_can_list_users(self, client: TestClient, session: Session):
        """拥有 user:read 权限的用户可以查看用户列表。"""
        headers = _create_user_with_custom_role(session, "rbac_user_reader@test.com", "rbac_reader", [("user", "read")])
        response = client.get(f"{settings.API_V1_STR}/admin/users/", headers=headers)
        assert response.status_code == 200

    def test_user_without_read_permission_cannot_list_users(self, client: TestClient, session: Session):
        """没有 user:read 权限的用户无法查看用户列表。"""
        headers = _create_user_with_custom_role(session, "rbac_no_user_read@test.com", "rbac_no_read", [("dashboard", "read")])
        response = client.get(f"{settings.API_V1_STR}/admin/users/", headers=headers)
        assert_error(response, 403)

    def test_user_with_create_permission_can_create_user(self, client: TestClient, session: Session):
        """拥有 user:create 权限的用户可以创建用户。"""
        assignable_role = Role(name="rbac_assignable", description="Assignable test role")
        session.add(assignable_role)
        session.commit()

        headers = _create_user_with_custom_role(session, "rbac_user_creator@test.com", "rbac_creator", [("user", "create")])
        response = client.post(
            f"{settings.API_V1_STR}/admin/users/",
            headers=headers,
            json={"email": "rbac_created@test.com", "password": "testpassword123", "roles": ["rbac_assignable"]},
        )
        assert response.status_code == 201

    def test_user_without_delete_permission_cannot_delete(self, client: TestClient, session: Session):
        """没有 user:delete 权限的用户无法删除用户。"""
        headers = _create_user_with_custom_role(session, "rbac_no_delete@test.com", "rbac_no_del", [("user", "read")])
        fake_id = uuid.uuid4()
        response = client.delete(f"{settings.API_V1_STR}/admin/users/{fake_id}", headers=headers)
        assert_error(response, 403)


class TestRBACDashboardAndAuditLog:
    """仪表盘和审计日志 RBAC 测试。"""

    def test_user_with_dashboard_read_can_access(self, client: TestClient, session: Session):
        """拥有 dashboard:read 权限的用户可以查看仪表盘。"""
        headers = _create_user_with_custom_role(session, "rbac_dash@test.com", "rbac_dash", [("dashboard", "read")])
        response = client.get(f"{settings.API_V1_STR}/admin/dashboard/stats", headers=headers)
        assert response.status_code == 200

    def test_user_without_dashboard_read_cannot_access(self, client: TestClient, session: Session):
        """没有 dashboard:read 权限的用户无法查看仪表盘。"""
        headers = _create_user_with_custom_role(session, "rbac_no_dash@test.com", "rbac_no_dash", [("user", "read")])
        response = client.get(f"{settings.API_V1_STR}/admin/dashboard/stats", headers=headers)
        assert_error(response, 403)

    def test_user_with_audit_read_can_access(self, client: TestClient, session: Session):
        """拥有 audit_log:read 权限的用户可以查看审计日志。"""
        headers = _create_user_with_custom_role(session, "rbac_audit@test.com", "rbac_audit", [("audit_log", "read")])
        response = client.get(f"{settings.API_V1_STR}/admin/audit-logs/", headers=headers)
        assert response.status_code == 200

    def test_user_without_audit_read_cannot_access(self, client: TestClient, session: Session):
        """没有 audit_log:read 权限的用户无法查看审计日志。"""
        headers = _create_user_with_custom_role(session, "rbac_no_audit@test.com", "rbac_no_audit", [("user", "read")])
        response = client.get(f"{settings.API_V1_STR}/admin/audit-logs/", headers=headers)
        assert_error(response, 403)
