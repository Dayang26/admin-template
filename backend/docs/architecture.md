# 后端项目架构分析报告

> 项目名称：nos-agent-carrier (Admin Boilerplate)
> 分析日期：2026-04-29
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

本项目是一个基于 **FastAPI** 的高标准 RESTful 后端服务模板 (Admin Boilerplate)，旨在为任何现代 SaaS 或中后台管理系统提供开箱即用的底座。核心功能包括：

- 用户身份认证（JWT OAuth2）
- 细粒度的、基于资源与操作的访问控制（RBAC）
- 完整的用户与角色权限管理体系
- 系统操作审计日志（Audit Logs）
- 数据大盘统计（Dashboard）
- 全局系统配置动态管理（System Settings）
- 分页查询与多维检索支持
- 统一 API 响应结构（中间件自动包装）

项目采用清晰的分层架构，将路由、业务逻辑、数据访问、模型定义各自分离，具备良好的可维护性与扩展性。

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

```text
backend/
├── app/
│   ├── main.py                   # FastAPI 应用入口
│   ├── alembic/                  # 数据库迁移
│   ├── api/
│   │   ├── main.py               # 路由聚合
│   │   └── routers/
│   │       ├── login.py          # 登录接口
│   │       ├── users.py          # 当前用户自服务接口
│   │       ├── system_settings.py# 公开系统配置接口
│   │       └── admin/
│   │           ├── users.py      # 用户管理接口
│   │           ├── roles.py      # 角色权限管理接口
│   │           ├── audit_logs.py # 审计日志接口
│   │           ├── system_settings.py # 系统全局设置管理接口
│   │           └── dashboard.py  # 仪表盘统计接口
│   ├── core/
│   │   ├── config.py             # 全局配置（pydantic-settings）
│   │   ├── db.py                 # 数据库引擎 & 初始化
│   │   └── security.py           # JWT & 密码工具
│   ├── deps/                     # 依赖注入集合
│   │   ├── audit.py              # 审计日志依赖
│   │   ├── auth.py               # 认证依赖
│   │   ├── db.py                 # 数据库会话依赖
│   │   └── permission.py         # RBAC 权限检查依赖
│   ├── middleware/
│   │   └── response.py           # 统一响应包装中间件
│   ├── models/
│   │   └── db/
│   │       ├── audit_log.py      # 审计日志表
│   │       ├── base.py           # 公共 Mixin（UUID PK、时间戳）
│   │       ├── user.py           # 用户表
│   │       ├── role.py           # 角色表
│   │       ├── permission.py     # 权限表
│   │       ├── userRole.py       # 用户-角色关联表
│   │       ├── rolePermission.py # 角色-权限关联表
│   │       └── system_setting.py # 系统全局设置表
│   ├── schemas/
│   │   ├── response.py           # 统一响应泛型模型 ApiResp[T]
│   │   ├── token.py              # Token 响应 Schema
│   │   ├── user.py               # 用户 Schema
│   │   ├── role.py               # 角色 Schema
│   │   └── system_setting.py     # 系统设置 Schema
│   └── services/
│       ├── login_service.py      # 登录业务逻辑
│       ├── user_service.py       # 用户管理业务逻辑
│       └── system_setting_service.py # 系统设置业务逻辑
├── tests/                        # 单元/集成测试
├── pyproject.toml                # 依赖管理 (uv)
└── alembic.ini                   # 迁移配置
```

---

## 4. 分层架构

采用标准 Web 三层架构 + 强依赖注入：

- **中间件层**：处理统一响应包装 (`UnifiedResponseMiddleware`)、CORS 以及全局异常拦截。
- **路由层 (routers)**：处理 HTTP 规范，接收请求并返回模型，纯调度，无复杂业务。
- **服务层 (services)**：封装所有业务逻辑，供路由层调用。
- **数据层 (models/db)**：由 SQLModel 定义关系与结构。
- **横切依赖 (deps)**：将 Auth 解析、DB 会话获取、RBAC 校验等抽离为 FastAPI 依赖项注入到路由中。

---

## 5. 数据库模型

所有表继承自基类及公共 Mixin，包含默认 UUID 主键及 `created_at`/`updated_at` 时间戳。

### 核心表结构

| 表名 | 模型类 | 职责 |
|------|--------|------|
| `t_user` | `User` | 用户，含邮箱、密码哈希、激活状态 |
| `t_role` | `Role` | 角色（如 superuser / admin 等） |
| `t_permission` | `Permission` | 最小权限单元，由 resource + action 唯一确定 |
| `t_user_role` | `UserRole` | 用户与角色关联（多对多中间表） |
| `t_role_permission` | `RolePermission` | 角色与权限关联（多对多中间表） |
| `t_audit_log` | `AuditLog` | 审计日志，记录关键操作轨迹、IP、UserAgent 等 |
| `t_system_setting` | `SystemSetting` | 系统全局参数表（极简 Key-Value 或宽表模式存储配置） |

### 关系简图

```
t_user ──(1:N)── t_user_role ──(N:1)── t_role ──(1:N)── t_role_permission ──(N:1)── t_permission
```

---

## 6. RBAC 权限系统

系统采用了纯粹且强大的基于角色的访问控制模型（Role-Based Access Control），彻底告别硬编码的“仅管理员可见”机制。

### 6.1 权限点设计
权限 (Permission) 是最小管控单元，由两部分组合：
- `resource`: 目标资源（如 `"user"`, `"role"`, `"system_setting"`）
- `action`: 行为动作（如 `"create"`, `"read"`, `"update"`, `"delete"`）

### 6.2 校验机制
依赖注入 `require_permission(resource, action)` 被挂载到每个路由上：
1. **超级特权**：判断当前用户是否含有系统内置的 `superuser` 角色，若有则直接放行。
2. **常规校验**：查询当前用户所挂载的所有角色，校验是否至少有一个角色包含了目标权限。如果全无，则抛出 `HTTP 403 Forbidden`。

这种设计使得非超级管理员也能被灵活授予“仅查看审计日志”或“可管理部分用户”的特权。

---

## 7. API 路由

路由按照业务域拆分，均在 `/api/v1` 前缀下：

### 认证与自服务
- `POST /login/access-token`: JWT 登录。
- `GET /users/me`: 获取个人信息。
- `PATCH /users/me` / `PATCH /users/me/password`: 更新资料或修改密码。

### 管理端体系 (Admin) - 均受 RBAC 保护
- `GET /admin/dashboard/stats`: 大盘指标统计。
- `GET/POST/PATCH/DELETE /admin/users`: 用户的全生命周期 CRUD，包含搜索与过滤。
- `GET /admin/roles`: 角色与权限查询。
- `GET /admin/audit-logs`: 审计追踪。
- `GET/PATCH /admin/system-settings`: 获取或更新后台系统配置。

### 开放数据
- `GET /system-settings/public`: 对未登录游客开放的基础信息（系统名称、Logo、备案号等）。

---

## 8. 统一响应结构

为简化前端数据解析，使用**中间件级**统一数据包装：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

机制：
- 路由处理函数仍直接返回 ORM 对象或普通 dict。
- `UnifiedResponseMiddleware` 捕获正常的 `2xx` 响应，自动嵌套一层 `ApiResp`。
- 全局异常处理器 (ExceptionHandler) 捕获 4xx/5xx，输出对应 code 且 data 为 `null`。
- 特例：遵循 OAuth2 标准的 `/login/access-token` 豁免包装。

---

## 9. 测试架构

后端具备极高的测试标准，测试覆盖率要求 100%。

- **测试组件**：`pytest` + `pytest-cov`
- **隔离机制**：
  - 测试期间，依赖覆盖会将 `get_db` 替换为测试专用的数据库。
  - 使用 `fastapi.testclient.TestClient` 模拟 HTTP 请求。
- **防时序攻击测试**：确保在账户不存在时，认证模块依然消耗相同计算周期以防扫描。

```bash
# 启动测试
cd backend && uv run pytest --cov=app tests/
```

---

## 10. 部署与启动

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

`lifespan` 生命周期钩子会在应用启动前自动执行 `init_db()`，实现：
1. 检查并补全系统所需的默认权限（`user:read` 等）。
2. 初始化根管理员角色与默认账户（账号密码从 `.env` 获取）。
3. 这保证了容器化或一键部署时环境开箱即用。
