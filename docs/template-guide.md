# 模板使用指南

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
9. [项目结构速查](#9-项目结构速查)
10. [常见问题](#10-常见问题)

---

## 1. 项目概览

这是一个前后端分离的管理后台模板，包含：

- **后端**：FastAPI + SQLModel + PostgreSQL，提供 RESTful API
- **前端**：React 19 + Vite + TypeScript + Shadcn/ui，纯 SPA 客户端渲染
- **内置功能**：用户管理、班级管理、角色权限管理（RBAC）、操作审计日志、仪表盘统计

技术栈：

| 层 | 技术 |
|----|------|
| 后端框架 | FastAPI |
| ORM | SQLModel (SQLAlchemy) |
| 数据库 | PostgreSQL |
| 认证 | JWT (PyJWT) |
| 密码哈希 | Argon2 + Bcrypt (pwdlib) |
| 前端框架 | React 19 + TypeScript |
| 构建工具 | Vite |
| UI 组件 | Shadcn/ui (Radix UI + Tailwind CSS) |
| 路由 | React Router v7 |
| 数据请求 | TanStack Query |
| 包管理 | uv (后端) / pnpm (前端) |

---

## 2. 环境要求

| 工具 | 最低版本 | 说明 |
|------|---------|------|
| Python | 3.12+ | 后端运行时 |
| Node.js | 18+ | 前端构建 |
| pnpm | 8+ | 前端包管理 |
| PostgreSQL | 14+ | 数据库 |
| uv | 最新 | Python 包管理（推荐，也可用 pip） |

---

## 3. 快速开始

### 3.1 克隆项目

```bash
git clone <your-repo-url>
cd nos_agent_carrier
```

### 3.2 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，至少修改以下配置：

```dotenv
# 数据库连接（确保 PostgreSQL 已运行）
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=你的数据库密码

# 安全密钥（生产环境必须修改）
SECRET_KEY=你的随机密钥

# 首个超级管理员账号
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=至少8位的密码

# 前端地址（开发环境）
FRONTEND_HOST=http://localhost:5173
```

### 3.3 启动后端

```bash
cd backend

# 创建虚拟环境并安装依赖
uv sync

# 创建数据库（如果还没有）
# 在 PostgreSQL 中执行：CREATE DATABASE app;

# 运行数据库迁移
uv run alembic -c app/alembic.ini upgrade head

# 启动开发服务器
uv run uvicorn app.main:app --reload
```

后端启动后：
- API 地址：http://localhost:8000
- Swagger 文档：http://localhost:8000/docs
- 首次启动会自动初始化内置角色、权限和超级管理员账号

### 3.4 启动前端

```bash
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

前端启动后：
- 访问 http://localhost:5173
- Vite 会自动将 `/api` 请求代理到后端 http://localhost:8000

### 3.5 登录

使用 `.env` 中配置的超级管理员账号登录：
- 邮箱：`FIRST_SUPERUSER` 的值
- 密码：`FIRST_SUPERUSER_PASSWORD` 的值

---

## 4. 数据库迁移

项目使用 Alembic 管理数据库 Schema 版本。

### 常用命令

```bash
cd backend

# 应用所有迁移（建表）
uv run alembic -c app/alembic.ini upgrade head

# 回滚一个版本
uv run alembic -c app/alembic.ini downgrade -1

# 生成新迁移（修改模型后）
uv run alembic -c app/alembic.ini revision --autogenerate -m "描述你的变更"
```

### 注意事项

- 迁移脚本位于 `backend/app/alembic/versions/`
- 自动生成的迁移可能需要手动检查和调整
- 如果迁移脚本中出现 `sqlmodel` 未定义的错误，在脚本顶部加上 `import sqlmodel`

---

## 5. 首个管理员账号

后端首次启动时，`init_db()` 会自动执行以下初始化（幂等操作，重复执行不会重复创建）：

1. **创建内置角色**：`superuser`、`teacher`、`student`
2. **创建内置权限**：14 个权限（用户/班级/角色/审计日志/仪表盘的 CRUD）
3. **绑定角色权限**：superuser 拥有所有权限，teacher 拥有 `class:read`、`user:create`、`user:read`
4. **创建超级管理员**：使用 `.env` 中的 `FIRST_SUPERUSER` 和 `FIRST_SUPERUSER_PASSWORD`

如果需要修改初始管理员信息，修改 `.env` 后重启后端即可（已存在的用户不会被覆盖）。

---

## 6. 运行测试

### 后端测试

```bash
cd backend

# 运行全部测试
uv run pytest tests/ -v

# 运行特定模块
uv run pytest tests/api/admin/test_users.py -v

# 带覆盖率
uv run pytest tests/ --cov=app --cov-report=html
```

**测试数据库**：测试会自动创建 `app_test` 数据库（如果不存在），无需手动建库。每个测试函数使用独立的数据库事务，测试结束后自动回滚，不会污染数据。

**前提条件**：PostgreSQL 必须运行，且 `.env` 中的数据库连接配置正确。

### 前端构建检查

```bash
cd frontend

# TypeScript 编译 + Vite 构建
pnpm build
```

---

## 7. 权限模型说明

### 7.1 两层权限体系

本项目的权限分为两个独立维度：

```
┌─────────────────────────────────────────────┐
│  全局 RBAC（系统功能权限）                     │
│                                             │
│  用户 ──→ 全局角色 ──→ 权限                   │
│  (User)   (Role)      (Permission)          │
│                                             │
│  决定：能访问哪些系统功能模块                   │
│  例如：teacher 角色有 class:read 权限          │
│       → 可以查看班级列表                      │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  班级角色（业务数据）                          │
│                                             │
│  用户 ──→ 班级 + 班级内角色                    │
│  (User)   (Class)  (teacher/student)        │
│                                             │
│  决定：在某个班级里的身份                      │
│  例如：张三在"2026级1班"是 teacher             │
│       → 可以查看该班级的成员列表               │
└─────────────────────────────────────────────┘
```

**两者互不影响**：
- 全局角色是 student 的用户，可以在某个班级里担任 teacher（如研究生助教）
- 修改全局角色不会影响班级角色绑定
- 删除全局角色不会删除班级成员关系

### 7.2 内置角色和权限

**角色：**

| 角色 | 说明 | 是否内置 |
|------|------|---------|
| superuser | 超级管理员，自动拥有所有权限 | 是（不可删除） |
| teacher | 教师，默认有班级查看和用户查看/创建权限 | 是（不可删除） |
| student | 学生，默认只有用户查看权限 | 是（不可删除） |

**权限：**

| 资源 | 操作 | 说明 |
|------|------|------|
| user | create / read / update / delete | 用户管理 |
| class | create / read / update / delete | 班级管理 |
| role | create / read / update / delete | 角色管理 |
| audit_log | read | 审计日志查看 |
| dashboard | read | 仪表盘查看 |

### 7.3 权限检查机制

后端使用 `require_permission(resource, action)` 依赖注入：

```python
@router.get("/", dependencies=[Depends(require_permission("user", "read"))])
def get_users(...):
    ...
```

检查逻辑：
1. 用户是 superuser → 直接放行
2. 查询用户的全局角色 → 查询角色绑定的权限 → 是否包含目标权限
3. 无匹配 → 403

**角色管理路由例外**：`/admin/roles/*` 保持 `get_current_active_superuser` 硬编码，防止权限提升攻击。

### 7.4 前端权限控制

前端通过 `useAuth().hasPermission("user:read")` 判断当前用户是否有某个权限：
- 侧边栏菜单按权限过滤
- superuser 自动拥有所有权限

---

## 8. 如何扩展业务模块

以"添加一个课程管理模块"为例：

### 8.1 后端

**Step 1：定义数据模型**

```python
# backend/app/models/db/course.py
from sqlmodel import Field
from app.models.db.base import UUIDPrimaryKeyMixin, TimestampMixin

class Course(UUIDPrimaryKeyMixin, TimestampMixin, table=True):
    __tablename__ = "t_course"
    name: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=500)
```

在 `models/db/__init__.py` 中导出。

**Step 2：定义 Schema**

```python
# backend/app/schemas/course.py
class CourseCreateReq(SQLModel):
    name: str
    description: str | None = None

class CoursePublicResp(SQLModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
```

**Step 3：添加权限种子数据**

在 `backend/app/core/db.py` 的 `BUILTIN_PERMISSIONS` 中添加：

```python
{"resource": "course", "action": "create"},
{"resource": "course", "action": "read"},
{"resource": "course", "action": "update"},
{"resource": "course", "action": "delete"},
```

在 `ROLE_PERMISSION_MAP` 中给需要的角色分配权限。

**Step 4：创建路由**

```python
# backend/app/api/routers/admin/courses.py
@router.get("/", dependencies=[Depends(require_permission("course", "read"))])
def get_courses(...):
    ...

@router.post("/", dependencies=[Depends(require_permission("course", "create"))])
def create_course(...):
    ...
```

在 `api/main.py` 中注册路由。

**Step 5：生成数据库迁移**

```bash
uv run alembic -c app/alembic.ini revision --autogenerate -m "add_course_table"
uv run alembic -c app/alembic.ini upgrade head
```

**Step 6：添加审计日志**

在写操作路由中调用 `log_audit()`：

```python
from app.deps import AuditInfo
from app.deps.audit import log_audit

@router.post("/")
def create_course(*, session: SessionDep, data: CourseCreateReq, audit: AuditInfo):
    course = ...
    log_audit(session, action="创建课程", detail=f"课程: {data.name}", **audit, status_code=201)
    return Response.ok(data=..., code=201)
```

### 8.2 前端

**Step 1：类型定义**

```typescript
// frontend/src/lib/types/course.ts
export interface Course {
  id: string
  name: string
  description: string | null
  created_at: string
}
```

**Step 2：API + Hook**

```typescript
// frontend/src/lib/api/courses.ts
export async function getCourses() { ... }

// frontend/src/lib/hooks/use-courses.ts
export function useCourses() {
  return useQuery({ queryKey: ['courses'], queryFn: getCourses })
}
```

**Step 3：页面组件**

在 `frontend/src/pages/admin/courses/` 下创建 `list.tsx`、`create.tsx`、`detail.tsx`。

**Step 4：路由注册**

在 `frontend/src/router.tsx` 中添加懒加载路由。

**Step 5：侧边栏菜单**

在 `frontend/src/components/layout/admin-sidebar.tsx` 中添加：

```typescript
{
  title: '课程管理',
  url: '/admin/courses',
  icon: BookOpen,
  permissions: ['course:read'],
}
```

**Step 6：权限标签中文化**

在 `frontend/src/lib/utils/permission-labels.ts` 中添加：

```typescript
RESOURCE_LABELS: { course: '课程管理' }
```

---

## 9. 项目结构速查

```
nos_agent_carrier/
├── backend/
│   ├── app/
│   │   ├── api/routers/          # API 路由
│   │   │   ├── admin/            # 管理端路由（用户/班级/角色/审计/仪表盘）
│   │   │   ├── login.py          # 登录
│   │   │   ├── users.py          # 用户自服务（/me）
│   │   │   └── teacher.py        # 教师视角
│   │   ├── core/
│   │   │   ├── config.py         # 配置（从 .env 读取）
│   │   │   ├── db.py             # 数据库引擎 + 种子数据初始化
│   │   │   └── security.py       # JWT + 密码哈希
│   │   ├── deps/
│   │   │   ├── auth.py           # 认证依赖
│   │   │   ├── audit.py          # 审计日志依赖
│   │   │   ├── db.py             # 数据库会话依赖
│   │   │   └── permission.py     # 权限检查依赖
│   │   ├── models/db/            # SQLModel 数据模型
│   │   ├── schemas/              # Pydantic 请求/响应 Schema
│   │   ├── services/             # 业务逻辑层
│   │   ├── alembic/              # 数据库迁移
│   │   └── main.py               # FastAPI 应用入口
│   └── tests/                    # 后端测试
│
├── frontend/
│   ├── src/
│   │   ├── components/           # UI 组件
│   │   │   ├── ui/               # Shadcn/ui 基础组件
│   │   │   ├── layout/           # 布局组件（侧边栏/顶栏/主题/用户菜单）
│   │   │   └── shared/           # 共享组件（分页/确认弹窗/错误边界）
│   │   ├── layouts/              # 页面布局（Admin/Student/Auth）
│   │   ├── lib/
│   │   │   ├── api/              # API 调用封装
│   │   │   ├── auth/             # 认证上下文 + 路由守卫
│   │   │   ├── hooks/            # TanStack Query hooks
│   │   │   ├── types/            # TypeScript 类型定义
│   │   │   └── utils/            # 工具函数
│   │   ├── pages/                # 页面组件
│   │   ├── providers/            # 全局 Provider
│   │   ├── router.tsx            # 路由配置
│   │   └── main.tsx              # 入口
│   └── docs/                     # 前端文档
│
├── docs/                         # 项目级文档
└── .env.example                  # 环境变量模板
```

---

## 10. 常见问题

### Q: 启动后端报 `POSTGRES_PASSWORD` 错误

确保 `.env` 文件存在且 `POSTGRES_PASSWORD` 不是默认的 `changethis`（生产环境会校验）。开发环境设置 `ENVIRONMENT=local` 可以跳过部分校验。

### Q: 数据库迁移报错 `sqlmodel is not defined`

在迁移脚本顶部加上 `import sqlmodel`。这是 Alembic 自动生成迁移时的已知问题。

### Q: 前端 Shadcn/ui 组件安装到了错误目录

`components.json` 中的 aliases 使用 `@/` 前缀时，Shadcn CLI 可能会创建 `@/` 物理目录。安装后检查组件是否在 `src/components/ui/` 下，如果不在则手动移动。

### Q: 测试报数据库连接错误

确保 PostgreSQL 正在运行，且 `.env` 中的连接配置正确。测试会自动创建 `app_test` 数据库，不需要手动建库。

### Q: 前端登录后页面空白

检查后端是否正在运行。Vite 开发服务器会将 `/api` 请求代理到 `http://localhost:8000`，如果后端没启动，API 请求会失败。

### Q: 如何修改主题颜色

编辑 `frontend/src/index.css` 中的 CSS 变量。当前使用浅蓝色调（oklch 色彩空间），修改 `--primary` 相关变量即可。
