# 后端项目架构分析报告

> 项目名称：nos-agent-carrier  
> 分析日期：2026-04-15  
> Python 版本：>=3.12

---

## 目录

1. [项目概览](#1-项目概览)
2. [技术栈](#2-技术栈)
3. [目录结构](#3-目录结构)
4. [分层架构](#4-分层架构)
5. [数据库模型](#5-数据库模型)
6. [RBAC 权限系统](#6-rbac-权限系统)
7. [API 路由](#7-api-路由)
8. [统一响应结构](#8-统一响应结构)
9. [认证与安全](#9-认证与安全)
10. [依赖注入](#10-依赖注入)
11. [服务层](#11-服务层)
12. [Schema 定义](#12-schema-定义)
13. [数据库迁移](#13-数据库迁移)
14. [配置管理](#14-配置管理)
15. [测试架构](#15-测试架构)
16. [启动流程](#16-启动流程)
17. [待完善功能](#17-待完善功能)

---

## 1. 项目概览

本项目是一个基于 **FastAPI** 的 RESTful 后端服务，面向教育场景，核心功能包括：

- 用户身份认证（JWT OAuth2）
- 基于角色的访问控制（RBAC）
- 班级维度的细粒度权限管理
- 超级管理员用户管理
- 分页查询支持
- 统一 API 响应结构（中间件自动包装）

项目采用清晰的分层架构，将路由、业务逻辑、数据访问、模型定义各自分离，具备良好的可扩展性。

---

## 2. 技术栈

| 类别 | 技术 | 版本要求 |
|------|------|---------|
| Web 框架 | FastAPI | >=0.135.3 |
| ORM / 数据模型 | SQLModel | >=0.0.38 |
| 数据库驱动 | psycopg (PostgreSQL) | >=3.2.0 |
| 数据库迁移 | Alembic | >=1.18.4 |
| 密码哈希 | pwdlib (Argon2 + Bcrypt) | >=0.3.0 |
| JWT 认证 | PyJWT | >=2.12.1 |
| 配置管理 | pydantic-settings | >=2.13.1 |
| 数据验证 | Pydantic | >=2.12.5 |
| 分页 | fastapi-pagination | >=0.15.12 |
| ASGI 服务器 | Uvicorn | >=0.44.0 |
| 测试框架 | Pytest | >=9.0.3 |
| 代码检查 | Ruff | >=0.15.10 |

---

## 3. 目录结构

```
backend/
├── app/
│   ├── main.py                   # FastAPI 应用入口
│   ├── alembic/                  # 数据库迁移
│   │   ├── env.py
│   │   └── versions/             # 迁移脚本
│   ├── api/
│   │   ├── main.py               # 路由聚合
│   │   └── routers/
│   │       ├── login.py          # 登录接口
│   │       ├── users.py          # 普通用户接口
│   │       └── admin/
│   │           └── users.py      # 管理员用户接口
│   ├── core/
│   │   ├── config.py             # 全局配置（pydantic-settings）
│   │   ├── db.py                 # 数据库引擎 & 初始化
│   │   └── security.py           # JWT & 密码工具
│   ├── deps/
│   │   ├── __init__.py           # 统一导出
│   │   ├── auth.py               # 认证依赖
│   │   ├── db.py                 # 数据库会话依赖
│   │   └── permission.py         # 权限检查依赖
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── response.py           # 统一响应包装中间件
│   ├── models/
│   │   ├── Token.py              # JWT Payload 模型
│   │   └── db/
│   │       ├── base.py           # 公共 Mixin（UUID PK、时间戳）
│   │       ├── user.py           # 用户表
│   │       ├── role.py           # 角色表
│   │       ├── permission.py     # 权限表
│   │       ├── userRole.py       # 用户-角色关联表
│   │       ├── rolePermission.py # 角色-权限关联表
│   │       └── userClass.py      # 班级表
│   ├── schemas/
│   │   ├── response.py           # 统一响应泛型模型 ApiResp[T]
│   │   ├── token.py              # Token 响应 Schema
│   │   └── user.py               # 用户 Schema
│   └── services/
│       ├── login_service.py      # 登录业务逻辑
│       └── user_service.py       # 用户业务逻辑
├── tests/
│   ├── conftest.py               # 全局测试 fixtures
│   ├── api/
│   │   ├── login/                # 登录接口测试
│   │   └── admin/                # 管理员接口测试
│   ├── core/                     # 核心模块测试
│   └── services/
│       └── test_login_service.py # 服务层单元测试
├── docs/                         # 项目文档
├── pyproject.toml                # 项目依赖与工具配置
└── alembic.ini                   # Alembic 配置文件
```

---

## 4. 分层架构

```
┌─────────────────────────────────────────┐
│              HTTP 请求                   │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│     CORSMiddleware（跨域处理）            │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│  UnifiedResponseMiddleware（统一响应包装） │
│  + 异常处理器（HTTPException / 422 / 500）│
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│           API 路由层 (routers)            │
│  login.py / users.py / admin/users.py   │
└──────────────────┬──────────────────────┘
                   │ 调用
┌──────────────────▼──────────────────────┐
│           服务层 (services)               │
│   login_service.py / user_service.py    │
└──────────────────┬──────────────────────┘
                   │ 调用
┌──────────────────▼──────────────────────┐
│         数据模型层 (models/db)             │
│  User / Role / Permission / UserRole …  │
└──────────────────┬──────────────────────┘
                   │ ORM
┌──────────────────▼──────────────────────┐
│          PostgreSQL 数据库                │
└─────────────────────────────────────────┘
```

横切关注点（通过 FastAPI 依赖注入 + 中间件）：

- `middleware/response.py` → 统一响应包装
- `deps/auth.py` → 身份认证
- `deps/db.py` → 数据库会话
- `deps/permission.py` → 权限检查

每一层职责清晰：

- **中间件层**：统一响应包装、异常处理、CORS 等横切逻辑
- **路由层**：处理 HTTP 请求/响应，参数校验，调用服务层
- **服务层**：封装业务逻辑，不直接暴露给 HTTP 层
- **模型层**：SQLModel 表定义，同时作为 ORM 实体和 Pydantic 模型
- **依赖层**：通过 FastAPI DI 系统注入认证、会话、权限等横切逻辑

---

## 5. 数据库模型

### 5.1 公共 Mixin（base.py）

所有表通过 Mixin 复用公共字段：

| Mixin | 字段 | 说明 |
|-------|------|------|
| `UUIDPrimaryKeyMixin` | `id: UUID` | 自动生成 UUID 主键，带索引 |
| `TimestampMixin` | `created_at`, `updated_at` | 带时区的创建/更新时间，`updated_at` 由数据库 `onupdate` 自动维护 |

### 5.2 数据表一览

| 表名 | 模型类 | 说明 |
|------|--------|------|
| `t_user` | `User` | 用户，含邮箱、密码哈希、激活状态 |
| `t_role` | `Role` | 角色，如 superuser / teacher / student |
| `t_permission` | `Permission` | 权限，由 resource + action 唯一确定 |
| `t_class` | `Class` | 班级，用于班级维度的角色绑定 |
| `t_user_role` | `UserRole` | 用户-角色关联，支持全局或班级级别 |
| `t_role_permission` | `RolePermission` | 角色-权限关联 |

### 5.3 实体关系图

```
t_user ──────────── t_user_role ──────────── t_role
  │                      │
  │                      │
t_class              t_role_permission
  │
t_permission
```

### 5.4 关键设计

**User（t_user）**

```
id            UUID PK
email         唯一索引，最长 255
is_active     布尔，默认 True
full_name     可选，最长 255
hashed_password 哈希后的密码
created_at / updated_at  时间戳
```

**UserRole（t_user_role）**

```
id        UUID PK
user_id   FK → t_user.id
role_id   FK → t_role.id
class_id  FK → t_class.id（可为 NULL）
唯一约束：(user_id, role_id, class_id)
```

`class_id IS NULL` 表示全局角色；非 NULL 表示该角色仅在指定班级内生效。

**Permission（t_permission）**

```
id        UUID PK
resource  资源名，如 class / user
action    操作名，如 create / read / update / delete
唯一约束：(resource, action)
```

---

## 6. RBAC 权限系统

### 6.1 设计模型

项目实现了一套 **RBAC（基于角色的访问控制）** 系统，并在此基础上扩展了**班级维度**的权限隔离：

```
用户 (User)
└── 拥有多个 UserRole（全局 或 班级级别）
    └── 每个 UserRole 关联一个 Role
        └── Role 拥有多个 Permission（resource + action）
```

### 6.2 两类角色

| 类型 | class_id | 说明 |
|------|----------|------|
| 全局角色 | NULL | 对所有资源生效，如 superuser |
| 班级角色 | 指定班级 UUID | 仅在该班级范围内生效，如 teacher in class A |

### 6.3 权限检查流程（require_permission）

```python
# deps/permission.py
def require_permission(resource: str, action: str):
    def checker(session, current_user):
        # 1. 检查是否拥有 superuser 全局角色 → 直接放行
        # 2. 查询用户角色链上是否存在匹配的 Permission
        #    (resource == resource AND action == action)
        # 3. 无匹配 → 403 Insufficient permissions
```

### 6.4 超级用户（superuser）

`get_current_active_superuser` 依赖专门检查用户是否拥有名为 `"superuser"` 的角色，用于保护管理员专属接口。

---

## 7. API 路由

### 7.1 路由前缀

所有接口统一挂载在 `/api/v1` 前缀下（由 `settings.API_V1_STR` 控制）。

### 7.2 接口列表

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| POST | `/api/v1/login/access-token` | 无 | 用户登录，返回 JWT |
| POST | `/api/v1/users/` | require_permission("user","create") | 创建用户（普通权限） |
| GET | `/api/v1/admin/users/` | superuser 角色 | 分页获取用户列表 |
| POST | `/api/v1/admin/users/` | superuser 角色 | 管理员创建用户并分配角色 |
| PATCH | `/api/v1/admin/users/{user_id}` | superuser 角色 | 管理员更新用户信息 |

### 7.3 路由聚合（api/main.py）

```python
api_router = APIRouter()
api_router.include_router(users_router)       # /users
api_router.include_router(login_router)       # /login
api_router.include_router(admin_users_router) # /admin/users
```

### 7.4 分页响应格式

管理员用户列表接口使用 `fastapi-pagination`，分页数据包装在统一响应的 `data` 字段内：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5
  }
}
```

---

## 8. 统一响应结构

### 8.1 设计目标

所有 API 接口（成功 & 失败）返回统一的 JSON 结构，方便前端统一处理。

### 8.2 响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | `int` | 与 HTTP 状态码一致 |
| `message` | `str` | 成功时为 `"success"`，失败时为错误描述 |
| `data` | `T \| null` | 成功时为业务数据，失败时为 `null` |

### 8.3 实现机制

采用**两层机制**，路由函数代码**零改动**：

| 层级 | 组件 | 职责 |
|------|------|------|
| 层 1 | `UnifiedResponseMiddleware` | 拦截 2xx JSON 响应，包装为 `{code, message, data}` |
| 层 2 | 异常处理器 | 覆盖 `HTTPException`、`RequestValidationError`、`Exception`，统一返回错误格式 |

**关键设计：**

- **自动化**：中间件自动包装，路由函数无需手动构造外层结构
- **防双重包装**：检测 body 是否已含 `code` + `data` 键
- **HTTP 状态码不变**：HTTP 状态码仍然语义正确，`code` 字段为冗余镜像
- **非 JSON 透传**：非 `application/json` 响应原样返回

### 8.4 Schema 定义

`schemas/response.py` 提供泛型模型 `ApiResp[T]`，供类型提示使用：

```python
class ApiResp(BaseModel, Generic[T]):
    code: int
    message: str
    data: T | None = None
```

---

## 9. 认证与安全

### 9.1 认证流程

```
客户端 POST /login/access-token
  → login_service.authenticate()
    → 查询用户（邮箱）
    → verify_password()（Argon2/Bcrypt）
    → 返回 User 对象
    → create_access_token(user.id)
    → JWT payload: { sub: user_id, exp: ... }
    → 返回 { access_token, token_type: "bearer" }

后续请求携带 Authorization: Bearer <token>
  → get_current_user()
    → jwt.decode()
    → session.get(User, token_data.sub)
    → 返回 User 对象
```

### 9.2 密码哈希策略

使用 `pwdlib` 支持双算法：

- **主算法**：Argon2（内存困难，更安全）
- **兼容算法**：Bcrypt（向后兼容旧哈希）
- **自动升级**：`verify_and_update()` 在验证成功后，若哈希算法过时则自动返回新哈希，服务层检测到后立即更新数据库

### 9.3 防时序攻击

用户不存在时，仍执行一次 `verify_password(password, DUMMY_HASH)`，避免通过响应时间差枚举有效邮箱。

### 9.4 JWT 配置

| 参数 | 值 |
|------|----|
| 算法 | HS256 |
| 默认有效期 | 60 × 24 × 8 分钟（8 天） |
| Payload | `{ sub: user_id, exp: timestamp }` |

---

## 10. 依赖注入

FastAPI 的依赖注入系统贯穿整个项目，`deps/` 目录统一管理所有可复用依赖：

### 10.1 SessionDep

```python
# deps/db.py
SessionDep = Annotated[Session, Depends(get_db)]
```

每个请求获得独立的 SQLModel `Session`，请求结束后自动关闭。

### 10.2 CurrentUser

```python
# deps/auth.py
CurrentUser = Annotated[User, Depends(get_current_user)]
```

解析 Bearer Token，查询并返回当前用户对象。Token 无效或用户不存在时抛出 403/404。

### 10.3 require_permission

```python
# deps/permission.py
Depends(require_permission("user", "create"))
```

工厂函数，返回一个检查特定 resource+action 权限的依赖。superuser 角色自动绕过权限检查。

### 10.4 get_current_active_superuser

```python
# deps/auth.py
Depends(get_current_active_superuser)
```

验证当前用户拥有 `"superuser"` 角色，用于管理员接口保护。

---

## 11. 服务层

### 11.1 login_service.py

| 函数 | 说明 |
|------|------|
| `authenticate(session, email, password)` | 验证邮箱+密码，返回 User 或 None；自动处理哈希升级 |

### 11.2 user_service.py

| 函数 | 说明 |
|------|------|
| `get_user_by_email(session, email)` | 按邮箱查询用户 |
| `create_user(session, user_create)` | 创建用户（哈希密码后存储） |
| `get_roles_by_names(session, role_names)` | 批量查询角色 |
| `create_user_with_roles(session, user_create)` | 创建用户并批量绑定角色，含完整校验 |

`create_user_with_roles` 的业务校验：

1. 邮箱唯一性检查
2. 角色存在性检查（返回缺失角色名）
3. 禁止分配 `"superuser"` 角色
4. 使用 `flush()` 先获取用户 ID，再批量插入 UserRole

---

## 12. Schema 定义

Schema 与数据库模型分离，用于 API 请求/响应的序列化与校验：

### 12.1 用户 Schema（schemas/user.py）

```
UserBase          email, is_active, full_name
└── UserCreate  + password (8-128 字符)
    └── UserCreateByAdmin  + password + roles: list[str]（至少1个）
    └── UserPublic  + id, created_at（响应用，不含密码）
UsersPublic       data: list[UserPublic], count: int
```

### 12.2 Token Schema（schemas/token.py）


```
TokenResp     access_token: str, token_type: str = "bearer"
TokenPayload  sub: str | None
```

---

### 12.3 响应 Schema（schemas/response.py）

```
ApiResp[T]    code: int, message: str, data: T | None
```

---

## 13. 数据库迁移

使用 **Alembic** 管理数据库 Schema 版本：

- 迁移脚本位于 `app/alembic/versions/`
- `env.py` 通过 `SQLModel.metadata` 自动感知所有模型变更
- 当前唯一迁移：`6e903e91a10e` — 创建全部 RBAC 相关表

**常用命令**

```bash
# 在 backend/ 目录下执行
alembic upgrade head          # 应用所有迁移
alembic downgrade -1          # 回滚一个版本
alembic revision --autogenerate -m "描述"  # 生成新迁移
```

---

## 14. 配置管理

`core/config.py` 使用 `pydantic-settings` 的 `BaseSettings`，支持从 `.env` 文件和环境变量读取配置：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `API_V1_STR` | `/api/v1` | API 前缀 |
| `SECRET_KEY` | 随机生成 | JWT 签名密钥 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 11520（8天） | Token 有效期 |
| `ENVIRONMENT` | `local` | 环境标识 |
| `POSTGRES_SERVER` | `localhost` | 数据库主机 |
| `POSTGRES_PORT` | `5432` | 数据库端口 |
| `POSTGRES_USER` | `postgres` | 数据库用户 |
| `POSTGRES_DB` | `""` | 数据库名 |
| `FIRST_SUPERUSER` | `admin@example.com` | 初始超级用户邮箱 |
| `FIRST_SUPERUSER_PASSWORD` | `changethis` | 初始超级用户密码 |
| `BACKEND_CORS_ORIGINS` | `[]` | 允许的跨域来源 |
| `FRONTEND_HOST` | `http://localhost:5173` | 前端地址（自动加入 CORS） |

**安全校验**：生产环境下若 `SECRET_KEY`、`POSTGRES_PASSWORD`、`FIRST_SUPERUSER_PASSWORD` 仍为默认值 `"changethis"`，启动时直接抛出 `ValueError`。

---

## 15. 测试架构

### 15.1 测试策略

项目包含两类测试：

| 类型 | 位置 | 说明 |
|------|------|------|
| 单元测试 | `tests/services/` | 使用 monkeypatch 隔离依赖，不访问数据库 |
| 集成测试 | `tests/api/` | 使用 TestClient + 真实数据库，测试完整请求链路 |

### 15.2 测试 Fixtures（conftest.py）

| Fixture | 作用域 | 说明 |
|---------|--------|------|
| `setup_test_database` | session | 通过 Alembic `upgrade head` 建表后执行 `init_db`（不在会话结束时删表） |
| `session` | function | 每个测试独立 Session，测试后自动 rollback |
| `client` | function | FastAPI TestClient，`raise_server_exceptions=False` |
| `superuser_token_headers` | function | 超级用户 JWT 请求头 |
| `normal_user_token_headers` | function | 普通用户（teacher 角色）JWT 请求头 |

### 15.3 测试辅助断言函数

| 函数 | 说明 |
|------|------|
| `assert_success(response, status_code)` | 断言成功响应，验证 code/message/data，返回 data |
| `assert_error(response, status_code, message)` | 断言错误响应，验证 code/data=null，可选验证 message |

### 15.4 依赖覆盖测试

通过 `app.dependency_overrides[get_db] = get_test_db` 将数据库会话替换为测试专用 Session，确保测试与生产数据库隔离。

### 15.5 测试覆盖范围

**登录接口（test_login_router.py）**

- 登录成功，验证 Token 返回
- 凭证错误返回 400
- 用户未激活返回 400
- 表单字段缺失返回 422

**管理员用户接口（test_users.py）**

- 超级用户获取用户列表（含排序验证）
- 分页参数测试
- 普通用户访问返回 403
- 未认证访问返回 401
- 创建用户成功（含角色分配）
- 邮箱重复返回 400
- 角色不存在返回 400
- 禁止分配 superuser 角色
- 权限不足返回 403

**登录服务（test_login_service.py）**

- 用户不存在时返回 None，且执行 dummy hash 防时序攻击
- 密码错误返回 None
- 密码正确且需要升级哈希时自动更新
- 密码正确且哈希无需升级时不触发写操作

---

## 16. 启动流程

```
uvicorn app.main:app

├── lifespan 钩子触发
│   └── init_db(session)
│       ├── 检查/创建内置角色（superuser / teacher / student）
│       ├── 检查/创建内置权限（class/user 的 CRUD）
│       ├── 检查/绑定角色-权限关系
│       └── 检查/创建初始超级用户并绑定 superuser 角色
├── 注册 UnifiedResponseMiddleware（统一响应包装）
├── 注册 CORS 中间件（根据配置）
├── 注册异常处理器（HTTPException / RequestValidationError / Exception）
├── 挂载 api_router（前缀 /api/v1）
├── add_pagination(app)
└── 注册健康检查接口 GET /
```

`init_db` 是幂等的——每次启动都会检查，已存在则跳过，不会重复创建。

---

## 17. 待完善功能

根据代码中的 `# todo` 注释，以下功能尚未实现：

| 位置 | 待完善内容 |
|------|-----------|
| `api/routers/users.py` | 教师角色分页获取所在班级的用户列表 |
| `api/routers/users.py` | `create_user` 接口的后续业务逻辑 |
| `api/main.py` | 本地环境专用私有路由 |
| `app/main.py` | Sentry DSN 错误监控集成 |
| 整体 | 班级管理 CRUD 接口 |
| 整体 | 角色/权限管理接口 |
| 整体 | 用户个人信息接口（修改密码、更新资料等） |
