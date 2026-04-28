from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pydantic import PostgresDsn
from sqlalchemy import create_engine, text
from sqlmodel import Session, select

from app.core.config import settings
from app.core.db import init_db
from app.core.security import create_access_token, get_password_hash
from app.deps.db import get_db
from app.main import app
from app.models.db import Role, User, UserRole

# backend/app 目录的绝对路径，用于定位 alembic.ini
_APP_DIR = Path(__file__).resolve().parent.parent / "app"
_TEST_DB_NAME = "app_test"


# ---------------------------------------------------------------------------
# 1. 自动创建测试数据库（如果不存在）
# ---------------------------------------------------------------------------
def _ensure_test_database() -> None:
    """连接到默认 postgres 数据库，检查并创建测试数据库。"""
    admin_url = PostgresDsn.build(
        scheme="postgresql+psycopg",
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        path="postgres",
    )
    admin_engine = create_engine(str(admin_url), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
            {"dbname": _TEST_DB_NAME},
        )
        if not result.scalar():
            conn.execute(text(f'CREATE DATABASE "{_TEST_DB_NAME}"'))
    admin_engine.dispose()


_ensure_test_database()

# ---------------------------------------------------------------------------
# 2. 构建指向 app_test 的测试引擎
# ---------------------------------------------------------------------------
test_url = PostgresDsn.build(
    scheme="postgresql+psycopg",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_SERVER,
    port=settings.POSTGRES_PORT,
    path=_TEST_DB_NAME,
)
test_engine = create_engine(str(test_url))


# ---------------------------------------------------------------------------
# 2. Session 级 fixture：用 Alembic 建表 + 初始化基础数据（整个测试会话只跑一次）
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    """
    以编程方式调用 alembic upgrade head，保证测试库表结构与开发/生产一致。
    不再使用 create_all / drop_all。
    """
    alembic_cfg = Config(str(_APP_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(_APP_DIR / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", str(test_url))
    command.upgrade(alembic_cfg, "head")

    # 初始化基础数据（superuser + superuser role），init_db 内部有幂等判断
    with Session(test_engine) as session:
        init_db(session)

    yield
    # 测试结束后不删表，表结构永远保留在测试库中


# ---------------------------------------------------------------------------
# 3. Function 级 fixture：嵌套事务隔离（每个测试函数独立回滚）
# ---------------------------------------------------------------------------
@pytest.fixture()
def session() -> Generator[Session, None, None]:
    """
    核心隔离机制：外层事务 + Savepoint。

    - connection.begin()  → 外层事务（永远不提交）
    - Session(join_transaction_mode="create_savepoint")
      → session.commit() 只在 savepoint 内部提交
    - transaction.rollback() → 测试结束，一切回滚
    """
    with test_engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
            # 动态覆盖 FastAPI 的 get_db 依赖，让 API 端点也使用同一个连接和事务
            def _override_get_db() -> Generator[Session, None, None]:
                yield session

            app.dependency_overrides[get_db] = _override_get_db
            yield session

        # 无条件回滚外层事务，所有脏数据灰飞烟灭
        transaction.rollback()

    # 恢复原始依赖
    app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# 4. Client fixture
# ---------------------------------------------------------------------------
@pytest.fixture()
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# 5. Token headers 辅助函数 & fixtures
#    改为接收 session 参数，确保在同一个事务内操作
# ---------------------------------------------------------------------------
def _get_superuser_token_headers(session: Session) -> dict[str, str]:
    superuser = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
    if not superuser:
        raise RuntimeError("Superuser not found. Ensure init_db has been called.")
    access_token = create_access_token(subject=superuser.id)
    return {"Authorization": f"Bearer {access_token}"}


def _get_normal_user_token_headers(session: Session) -> dict[str, str]:
    # 创建 "teacher" 角色
    teacher_role = session.exec(select(Role).where(Role.name == "teacher")).first()
    if not teacher_role:
        teacher_role = Role(name="teacher", description="Teacher role")
        session.add(teacher_role)
        session.commit()
        session.refresh(teacher_role)

    # 创建普通用户
    normal_user = session.exec(select(User).where(User.email == "normal@example.com")).first()
    if not normal_user:
        normal_user = User(
            email="normal@example.com",
            hashed_password=get_password_hash("password1234"),
            is_active=True,
            full_name="Normal User",
        )
        session.add(normal_user)
        session.commit()
        session.refresh(normal_user)

    # 分配 teacher 角色
    existing_user_role = session.exec(
        select(UserRole).where(
            UserRole.user_id == normal_user.id,
            UserRole.role_id == teacher_role.id,
            UserRole.class_id.is_(None),
        )
    ).first()
    if not existing_user_role:
        session.add(UserRole(user_id=normal_user.id, role_id=teacher_role.id, class_id=None))
        session.commit()

    access_token = create_access_token(subject=normal_user.id)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture()
def superuser_token_headers(session: Session) -> dict[str, str]:
    return _get_superuser_token_headers(session)


@pytest.fixture()
def normal_user_token_headers(session: Session) -> dict[str, str]:
    return _get_normal_user_token_headers(session)


def assert_success(response, status_code: int = 200) -> dict:
    """断言响应为成功，返回 data 字段内容。"""
    assert response.status_code == status_code
    body = response.json()
    assert body["code"] == status_code
    assert body["message"] == "success"
    assert body["data"] is not None
    return body["data"]


def assert_error(response, status_code: int, message: str | None = None) -> None:
    """断言响应为错误，可选校验 message。"""
    assert response.status_code == status_code
    body = response.json()
    assert body["code"] == status_code
    assert body["data"] is None
    if message:
        assert body["message"] == message
