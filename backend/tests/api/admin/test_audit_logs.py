"""操作日志功能测试。

测试覆盖：
1. 登录操作记录日志
2. 创建用户记录日志
3. 更新用户记录日志
4. 删除用户记录日志
5. 更新个人资料记录日志
6. 修改密码记录日志
7. 日志查询接口（分页、筛选）
8. 非 superuser 无法查看日志
"""

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models.db import Role
from app.models.db.audit_log import AuditLog
from tests.conftest import assert_error, assert_success


def _count_audit_logs(session: Session, action: str | None = None) -> int:
    """统计审计日志数量。"""
    stmt = select(AuditLog)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    return len(session.exec(stmt).all())


def _get_latest_audit_log(session: Session, action: str | None = None) -> AuditLog | None:
    """获取最新的审计日志。"""
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc())
    if action:
        stmt = stmt.where(AuditLog.action == action)
    return session.exec(stmt).first()


def _ensure_assignable_role(session: Session) -> str:
    role_name = "audit_test_role"
    role = session.exec(select(Role).where(Role.name == role_name)).first()
    if not role:
        session.add(Role(name=role_name, description="Audit test role"))
        session.commit()
    return role_name


class TestLoginAuditLog:
    """登录操作日志测试。"""

    def test_login_success_creates_audit_log(self, client: TestClient, session: Session):
        """登录成功应记录审计日志。"""
        before_count = _count_audit_logs(session, action="用户登录")

        response = client.post(
            f"{settings.API_V1_STR}/login/access-token",
            data={
                "username": settings.FIRST_SUPERUSER,
                "password": settings.FIRST_SUPERUSER_PASSWORD,
            },
        )
        assert response.status_code == 200

        after_count = _count_audit_logs(session, action="用户登录")
        assert after_count == before_count + 1

        log = _get_latest_audit_log(session, action="用户登录")
        assert log is not None
        assert log.user_email == settings.FIRST_SUPERUSER
        assert log.method == "POST"
        assert "login" in log.path
        assert log.status_code == 200

    def test_login_failure_no_audit_log(self, client: TestClient, session: Session):
        """登录失败不应记录审计日志。"""
        before_count = _count_audit_logs(session, action="用户登录")

        response = client.post(
            f"{settings.API_V1_STR}/login/access-token",
            data={"username": "wrong@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 400

        after_count = _count_audit_logs(session, action="用户登录")
        assert after_count == before_count


class TestAdminUserAuditLog:
    """管理员用户操作日志测试。"""

    def test_create_user_creates_audit_log(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """创建用户应记录审计日志。"""
        role_name = _ensure_assignable_role(session)
        before_count = _count_audit_logs(session, action="创建用户")

        response = client.post(
            f"{settings.API_V1_STR}/admin/users/",
            headers=superuser_token_headers,
            json={
                "email": "audit_test_user@example.com",
                "password": "testpassword123",
                "roles": [role_name],
            },
        )
        assert response.status_code == 201

        after_count = _count_audit_logs(session, action="创建用户")
        assert after_count == before_count + 1

        log = _get_latest_audit_log(session, action="创建用户")
        assert log is not None
        assert "audit_test_user@example.com" in (log.detail or "")
        assert log.method == "POST"

    def test_update_user_creates_audit_log(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """更新用户应记录审计日志。"""
        role_name = _ensure_assignable_role(session)
        # 先创建一个用户
        create_resp = client.post(
            f"{settings.API_V1_STR}/admin/users/",
            headers=superuser_token_headers,
            json={
                "email": "audit_update_test@example.com",
                "password": "testpassword123",
                "roles": [role_name],
            },
        )
        user_id = create_resp.json()["data"]["id"]

        before_count = _count_audit_logs(session, action="更新用户")

        response = client.patch(
            f"{settings.API_V1_STR}/admin/users/{user_id}",
            headers=superuser_token_headers,
            json={"full_name": "审计测试用户"},
        )
        assert response.status_code == 200

        after_count = _count_audit_logs(session, action="更新用户")
        assert after_count == before_count + 1

        log = _get_latest_audit_log(session, action="更新用户")
        assert log is not None
        assert "姓名" in (log.detail or "")

    def test_delete_user_creates_audit_log(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """删除用户应记录审计日志。"""
        role_name = _ensure_assignable_role(session)
        # 先创建一个用户
        create_resp = client.post(
            f"{settings.API_V1_STR}/admin/users/",
            headers=superuser_token_headers,
            json={
                "email": "audit_delete_test@example.com",
                "password": "testpassword123",
                "roles": [role_name],
            },
        )
        user_id = create_resp.json()["data"]["id"]

        before_count = _count_audit_logs(session, action="删除用户")

        response = client.delete(
            f"{settings.API_V1_STR}/admin/users/{user_id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200

        after_count = _count_audit_logs(session, action="删除用户")
        assert after_count == before_count + 1

        log = _get_latest_audit_log(session, action="删除用户")
        assert log is not None
        assert "audit_delete_test@example.com" in (log.detail or "")


class TestSelfServiceAuditLog:
    """用户自服务操作日志测试。"""

    def test_update_profile_creates_audit_log(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """更新个人资料应记录审计日志。"""
        before_count = _count_audit_logs(session, action="更新个人资料")

        response = client.patch(
            f"{settings.API_V1_STR}/users/me",
            headers=superuser_token_headers,
            json={"full_name": "审计测试名字"},
        )
        assert response.status_code == 200

        after_count = _count_audit_logs(session, action="更新个人资料")
        assert after_count == before_count + 1

    def test_change_password_creates_audit_log(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """修改密码应记录审计日志。"""
        before_count = _count_audit_logs(session, action="修改密码")

        response = client.patch(
            f"{settings.API_V1_STR}/users/me/password",
            headers=superuser_token_headers,
            json={
                "current_password": settings.FIRST_SUPERUSER_PASSWORD,
                "new_password": settings.FIRST_SUPERUSER_PASSWORD,  # 改回原密码
            },
        )
        assert response.status_code == 200

        after_count = _count_audit_logs(session, action="修改密码")
        assert after_count == before_count + 1


class TestAuditLogQuery:
    """日志查询接口测试。"""

    def test_get_audit_logs_success(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """superuser 可以查看日志列表。"""
        response = client.get(
            f"{settings.API_V1_STR}/admin/audit-logs/",
            headers=superuser_token_headers,
        )
        data = assert_success(response)
        assert "items" in data
        assert "total" in data

    def test_get_audit_logs_filter_by_action(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """可以按操作类型筛选日志。"""
        # 先触发一个登录日志
        client.post(
            f"{settings.API_V1_STR}/login/access-token",
            data={
                "username": settings.FIRST_SUPERUSER,
                "password": settings.FIRST_SUPERUSER_PASSWORD,
            },
        )

        response = client.get(
            f"{settings.API_V1_STR}/admin/audit-logs/?action=用户登录",
            headers=superuser_token_headers,
        )
        data = assert_success(response)
        for item in data["items"]:
            assert item["action"] == "用户登录"

    def test_get_audit_logs_filter_by_email(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """可以按用户邮箱筛选日志。"""
        response = client.get(
            f"{settings.API_V1_STR}/admin/audit-logs/?user_email={settings.FIRST_SUPERUSER}",
            headers=superuser_token_headers,
        )
        data = assert_success(response)
        for item in data["items"]:
            assert settings.FIRST_SUPERUSER in item["user_email"]

    def test_non_superuser_cannot_view_audit_logs(self, client: TestClient, session: Session, normal_user_token_headers: dict):
        """非 superuser 无法查看日志。"""
        response = client.get(
            f"{settings.API_V1_STR}/admin/audit-logs/",
            headers=normal_user_token_headers,
        )
        assert_error(response, 403)

    def test_unauthenticated_cannot_view_audit_logs(self, client: TestClient):
        """未认证用户无法查看日志。"""
        response = client.get(f"{settings.API_V1_STR}/admin/audit-logs/")
        assert response.status_code in (401, 403)


class TestAuditLogFields:
    """日志字段完整性测试。"""

    def test_audit_log_has_all_fields(self, client: TestClient, session: Session, superuser_token_headers: dict):
        """审计日志应包含所有必要字段。"""
        # 触发一个操作
        client.patch(
            f"{settings.API_V1_STR}/users/me",
            headers=superuser_token_headers,
            json={"full_name": "字段测试"},
        )

        log = _get_latest_audit_log(session, action="更新个人资料")
        assert log is not None
        assert log.user_id is not None
        assert log.user_email is not None
        assert log.method == "PATCH"
        assert "/users/me" in log.path
        assert log.action == "更新个人资料"
        assert log.status_code == 200
        assert log.created_at is not None
        # IP 和 User-Agent 在测试环境中可能为 None 或 testclient
