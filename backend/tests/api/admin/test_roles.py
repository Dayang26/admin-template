"""角色管理接口测试。

测试覆盖：
1. 获取角色列表（含权限信息）
2. 创建自定义角色
3. 更新角色
4. 删除自定义角色
5. 内置角色禁止删除
6. 权限列表（只读）
7. 角色权限绑定（全量替换）
8. 权限控制（非 superuser 禁止访问）
"""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models.db import Role
from tests.conftest import assert_error, assert_success


class TestGetRoles:
    """获取角色列表测试。"""

    def test_get_roles_success(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """superuser 可以获取角色列表。"""
        response = client.get(
            f"{settings.API_V1_STR}/admin/roles/",
            headers=superuser_token_headers,
        )
        data = assert_success(response)
        assert isinstance(data, list)
        assert len(data) >= 1

        # 每个角色应包含 permissions 字段
        for role in data:
            assert "id" in role
            assert "name" in role
            assert "is_builtin" in role
            assert "permissions" in role

    def test_get_roles_includes_builtin_flag(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """内置角色应标记 is_builtin=True。"""
        response = client.get(
            f"{settings.API_V1_STR}/admin/roles/",
            headers=superuser_token_headers,
        )
        data = assert_success(response)
        builtin_names = {r["name"] for r in data if r["is_builtin"]}
        assert builtin_names == {"superuser"}

    def test_get_roles_forbidden(self, client: TestClient, session: Session, normal_user_token_headers: dict):
        """非 superuser 无法获取角色列表。"""
        response = client.get(
            f"{settings.API_V1_STR}/admin/roles/",
            headers=normal_user_token_headers,
        )
        assert_error(response, 403)


class TestCreateRole:
    """创建角色测试。"""

    def test_create_role_success(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """创建自定义角色成功。"""
        response = client.post(
            f"{settings.API_V1_STR}/admin/roles/",
            headers=superuser_token_headers,
            json={"name": "assistant", "description": "助教角色"},
        )
        data = assert_success(response, 201)
        assert data["name"] == "assistant"
        assert data["description"] == "助教角色"
        assert data["is_builtin"] is False

    def test_create_role_duplicate_name(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """角色名重复应返回 400。"""
        response = client.post(
            f"{settings.API_V1_STR}/admin/roles/",
            headers=superuser_token_headers,
            json={"name": "superuser"},
        )
        assert_error(response, 400)

    def test_create_role_empty_name(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """角色名为空应返回 400。"""
        response = client.post(
            f"{settings.API_V1_STR}/admin/roles/",
            headers=superuser_token_headers,
            json={"name": ""},
        )
        assert_error(response, 400)


class TestUpdateRole:
    """更新角色测试。"""

    def test_update_role_success(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """更新角色名称和描述。"""
        # 先创建
        create_resp = client.post(
            f"{settings.API_V1_STR}/admin/roles/",
            headers=superuser_token_headers,
            json={"name": "update_test_role"},
        )
        role_id = create_resp.json()["data"]["id"]

        response = client.patch(
            f"{settings.API_V1_STR}/admin/roles/{role_id}",
            headers=superuser_token_headers,
            json={"name": "updated_role", "description": "已更新"},
        )
        data = assert_success(response)
        assert data["name"] == "updated_role"
        assert data["description"] == "已更新"

    def test_update_role_not_found(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """更新不存在的角色返回 404。"""
        fake_id = str(uuid.uuid4())
        response = client.patch(
            f"{settings.API_V1_STR}/admin/roles/{fake_id}",
            headers=superuser_token_headers,
            json={"name": "whatever"},
        )
        assert_error(response, 404)


class TestDeleteRole:
    """删除角色测试。"""

    def test_delete_custom_role_success(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """删除自定义角色成功。"""
        create_resp = client.post(
            f"{settings.API_V1_STR}/admin/roles/",
            headers=superuser_token_headers,
            json={"name": "delete_test_role"},
        )
        role_id = create_resp.json()["data"]["id"]

        response = client.delete(
            f"{settings.API_V1_STR}/admin/roles/{role_id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        assert response.json()["code"] == 200

    def test_delete_builtin_role_forbidden(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """内置角色禁止删除。"""
        superuser_role = session.exec(select(Role).where(Role.name == "superuser")).first()
        assert superuser_role is not None

        response = client.delete(
            f"{settings.API_V1_STR}/admin/roles/{superuser_role.id}",
            headers=superuser_token_headers,
        )
        assert_error(response, 400)

    def test_delete_role_not_found(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """删除不存在的角色返回 404。"""
        fake_id = str(uuid.uuid4())
        response = client.delete(
            f"{settings.API_V1_STR}/admin/roles/{fake_id}",
            headers=superuser_token_headers,
        )
        assert_error(response, 404)


class TestPermissions:
    """权限相关测试。"""

    def test_get_permissions_success(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """获取权限列表成功。"""
        response = client.get(
            f"{settings.API_V1_STR}/admin/roles/permissions",
            headers=superuser_token_headers,
        )
        data = assert_success(response)
        assert isinstance(data, list)
        assert len(data) >= 8  # 8 个初始权限

        for perm in data:
            assert "id" in perm
            assert "resource" in perm
            assert "action" in perm

    def test_update_role_permissions_success(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """更新角色权限绑定成功。"""
        # 创建一个自定义角色
        create_resp = client.post(
            f"{settings.API_V1_STR}/admin/roles/",
            headers=superuser_token_headers,
            json={"name": "perm_test_role"},
        )
        role_id = create_resp.json()["data"]["id"]

        # 获取权限列表
        perms_resp = client.get(
            f"{settings.API_V1_STR}/admin/roles/permissions",
            headers=superuser_token_headers,
        )
        all_perms = perms_resp.json()["data"]
        # 选前两个权限
        perm_ids = [all_perms[0]["id"], all_perms[1]["id"]]

        # 绑定权限
        response = client.put(
            f"{settings.API_V1_STR}/admin/roles/{role_id}/permissions",
            headers=superuser_token_headers,
            json={"permission_ids": perm_ids},
        )
        data = assert_success(response)
        assert len(data["permissions"]) == 2

    def test_update_role_permissions_clear(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """传空数组清除角色所有权限。"""
        create_resp = client.post(
            f"{settings.API_V1_STR}/admin/roles/",
            headers=superuser_token_headers,
            json={"name": "perm_clear_role"},
        )
        role_id = create_resp.json()["data"]["id"]

        response = client.put(
            f"{settings.API_V1_STR}/admin/roles/{role_id}/permissions",
            headers=superuser_token_headers,
            json={"permission_ids": []},
        )
        data = assert_success(response)
        assert len(data["permissions"]) == 0

    def test_update_role_permissions_invalid_id(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """传不存在的权限 ID 返回 400。"""
        create_resp = client.post(
            f"{settings.API_V1_STR}/admin/roles/",
            headers=superuser_token_headers,
            json={"name": "perm_invalid_role"},
        )
        role_id = create_resp.json()["data"]["id"]

        fake_perm_id = str(uuid.uuid4())
        response = client.put(
            f"{settings.API_V1_STR}/admin/roles/{role_id}/permissions",
            headers=superuser_token_headers,
            json={"permission_ids": [fake_perm_id]},
        )
        assert_error(response, 400)
