# 模板使用指南 (Admin Boilerplate)

> 本文档面向 fork 本项目后进行二次开发的使用者。
> 阅读完本文档后，你应该能在 30 分钟内跑通整个项目。

---

## 目录

1. [项目概览](#1-项目概览)
2. [环境要求](#2-环境要求)
3. [快速开始](#3-快速开始)
4. [数据库迁移](#4-数据库迁移)
5. [首个管理员账号](#5-首个管理员账号)
6. [运行测试](#6-运行测试)
7. [权限模型说明](#7-权限模型说明)
8. [如何扩展业务模块](#8-如何扩展业务模块)

---

## 1. 项目概览

这是一个前后端分离、开箱即用的纯粹中后台管理底座（Admin Boilerplate），包含：

- **后端**：FastAPI + SQLModel + PostgreSQL，提供 RESTful API。
- **前端**：React 19 + Vite + TypeScript + Shadcn/ui，纯 SPA 客户端渲染。
- **内置功能**：用户管理、角色权限管理（RBAC）、操作审计日志、仪表盘统计、系统全局设置。

---

## 2. 环境要求

| 工具 | 最低版本 | 说明 |
|------|---------|------|
| Python | 3.12+ | 后端运行时 |
| Node.js | 18+ | 前端构建 |
| pnpm | 8+ | 前端包管理 |
| PostgreSQL | 14+ | 数据库 |
| uv | 最新 | Python 包管理（强烈推荐） |

---

## 3. 快速开始

### 3.1 环境变量

```bash
cp .env.example .env
```

编辑 `.env`，至少修改以下配置：

```dotenv
# 数据库连接
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=你的数据库密码

# 安全密钥
SECRET_KEY=你的随机密钥

# 首个超级管理员账号
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=至少8位的密码
```

### 3.2 启动后端

```bash
cd backend
# 使用 uv 同步依赖
uv sync
# 运行数据库迁移 (自动建表)
uv run alembic -c app/alembic.ini upgrade head
# 启动开发服务器
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3.3 启动前端

```bash
cd frontend
# 安装依赖
pnpm install
# 启动开发服务器
pnpm dev
```

前端启动后访问 `http://localhost:5173`。Vite 会自动将 `/api` 请求代理到后端。使用 `.env` 中配置的 `FIRST_SUPERUSER` 邮箱与密码即可登录系统。

---

## 4. 数据库迁移

项目使用 Alembic 管理数据库 Schema 版本。

```bash
cd backend

# 应用所有迁移
uv run alembic -c app/alembic.ini upgrade head

# 修改 Model 后生成新迁移脚本
uv run alembic -c app/alembic.ini revision --autogenerate -m "描述你的变更"
```

> **注意**：自动生成的迁移可能需要手动检查（特别是如果在脚本中出现 `sqlmodel` 未定义的错误，请在生成的文件顶部加上 `import sqlmodel`）。

---

## 5. 首个管理员账号

后端首次启动时，`init_db()` 会自动执行以下初始化（幂等操作）：

1. **创建内置角色**：`superuser`（系统超级管理员，不可删除）。
2. **创建内置权限**：初始化基础模块（用户、角色、审计日志、系统设置、仪表盘）的 CRUD 权限种子。
3. **创建超级管理员**：使用 `.env` 中的账号密码建立初代管理员，并挂载 `superuser` 角色。

如果后续需要重置初始管理员密码，直接修改 `.env` 并非一劳永逸，建议直接在系统的“个人中心”或通过超级管理员直接修改。

---

## 6. 运行测试

### 后端测试

```bash
cd backend
# 运行全部测试
uv run pytest tests/ -v
# 运行带覆盖率报告的测试
uv run pytest tests/ --cov=app --cov-report=html
```

测试会自动创建临时的 `app_test` 数据库，不会污染生产库数据。每个测试函数独立回滚事务。

### 前端构建检查

```bash
cd frontend
pnpm build
```

---

## 7. 权限模型说明

本项目实现了基于资源的全局 **RBAC（Role-Based Access Control）** 系统，彻底摒弃了接口层的硬编码角色。

### 7.1 模型链路

```text
用户 (User) ──(N:N)── 全局角色 (Role) ──(N:N)── 权限 (Permission)
```

### 7.2 最小管控单元 (Permission)

每个权限点由两个维度构成：
- `resource`: 目标资源名（例如 `"user"`, `"role"`, `"audit_log"`）
- `action`: 操作行为（例如 `"create"`, `"read"`, `"update"`, `"delete"`）

### 7.3 后端校验机制

在路由层通过 FastAPI 依赖注入校验权限：

```python
@router.get("/", dependencies=[Depends(require_permission("user", "read"))])
def get_users(...):
    pass
```

1. **超级特权**：如果当前用户挂载了 `superuser` 角色，直接越过底层检验放行。
2. **动态匹配**：系统查询当前用户挂载的所有角色，检查是否存在 `resource` 与 `action` 完全匹配的权限点。如无则抛出 `403 Forbidden`。

### 7.4 前端动态呈现

前端可通过 Hooks 直接判定权限以决定是否渲染按钮或菜单：
```typescript
const { hasPermission } = useAuth();

if (hasPermission("user:delete")) {
   // 渲染删除按钮
}
```

---

## 8. 如何扩展业务模块

请参阅我们单独的《[RBAC 扩展指南](./rbac-extension-guide.md)》，它详细讲述了如何从后端增加模型、权限点、路由，到前端增加数据 Hook 和菜单的一个完整生命周期流程。
