# NOS Agent Carrier 架构文档

> 项目状态：生产级后台管理模板
> 最后更新：2026-05-07

---

## 1. 项目概览

NOS Agent Carrier 是一个开箱即用的企业级中后台管理底座（Admin Boilerplate），采用前后端分离架构，为二次开发和快速业务迭代而设计。

**核心特性：**

- 前后端分离，SPA 单页应用
- 基于 JWT 的 OAuth2 认证体系
- 细粒度 RBAC 权限控制（资源 + 操作）
- 操作审计日志
- 动态系统品牌配置（Logo、名称、Favicon）
- 文件上传服务
- Docker 一键部署

---

## 2. 技术栈

### 后端

| 类别 | 技术 | 说明 |
|------|------|------|
| 框架 | FastAPI >= 0.135 | 高性能 ASGI 框架 |
| ORM | SQLModel >= 0.0.38 | SQLAlchemy + Pydantic 融合 |
| 数据库 | PostgreSQL >= 14 | 主数据存储 |
| 迁移 | Alembic >= 1.18 | 数据库版本管理 |
| 认证 | PyJWT >= 2.12 | JWT Token 签发与验证 |
| 密码哈希 | pwdlib (Argon2 + Bcrypt) | 安全密码存储 |
| 包管理 | uv | 高性能 Python 包管理 |
| 测试 | Pytest >= 9.0 | 单元与集成测试 |
| 代码检查 | Ruff | Python Linting |

### 前端

| 类别 | 技术 | 说明 |
|------|------|------|
| 框架 | React 19 | SPA 客户端渲染 |
| 构建 | Vite | 快速开发与生产构建 |
| 语言 | TypeScript | 严格类型检查（Strict Mode） |
| 路由 | React Router v7 | 客户端路由 |
| UI 库 | Shadcn/ui + Tailwind CSS v4 | 原子化组件库 |
| 状态/数据 | TanStack Query | 服务端状态管理 |
| 表单 | React Hook Form + Zod | 表单验证 |
| 包管理 | pnpm | Node.js 包管理 |

### 基础设施

| 类别 | 技术 | 说明 |
|------|------|------|
| 容器化 | Docker + Docker Compose | 环境一致性 |
| Web 服务器 | Uvicorn | ASGI 应用服务器 |

---

## 3. 系统架构

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client (Browser)                         │
│                    React 19 + TypeScript SPA                    │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTP/HTTPS (REST API)
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Routers   │  │  Services   │  │   Models    │             │
│  │  (API Layer) │  │ (Business)  │  │    (ORM)    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    Deps     │  │   Schemas   │  │    Core     │             │
│  │ (Dependency)│  │ (Validation)│  │ (Config/Sec)│             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │ SQL
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                           │
│  t_user | t_role | t_permission | t_audit_log | t_system_setting │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 前端架构图

```
┌──────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      Router (React Router v7)            │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │   │
│  │  │AuthLayout│  │AdminLayout│  │   Route Guards       │   │   │
│  │  └──────────┘  └──────────┘  │   (RequireAuth)      │   │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     State Management                     │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ AuthContext  │  │TanStack Query│  │ ThemeContext  │  │   │
│  │  │(Auth State)  │  │(Server Cache) │  │(Light/Dark)  │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        Components                        │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────┐    │   │
│  │  │   UI (sh)  │  │  Layout     │  │  Shared        │    │   │
│  │  │  Buttons   │  │ Sidebar     │  │  ConfirmDialog │    │   │
│  │  └────────────┘  └────────────┘  └────────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. 后端架构

### 4.1 目录结构

```
backend/
├── app/
│   ├── main.py                      # FastAPI 应用入口 (lifespan 钩子)
│   ├── alembic/                     # 数据库迁移配置
│   │   ├──.ini
│   │   └── versions/                # 迁移脚本版本
│   ├── api/
│   │   ├── main.py                  # 路由聚合入口
│   │   └── routers/
│   │       ├── login.py             # 登录认证
│   │       ├── users.py             # 当前用户自服务
│   │       ├── system_settings.py   # 公开系统配置
│   │       └── admin/               # 管理端 API
│   │           ├── users.py         # 用户管理
│   │           ├── roles.py         # 角色管理
│   │           ├── permissions.py   # 权限管理
│   │           ├── audit_logs.py     # 审计日志
│   │           ├── dashboard.py     # 仪表盘统计
│   │           ├── upload.py        # 文件上传
│   │           └── system_settings.py # 系统设置管理
│   ├── core/
│   │   ├── config.py                # pydantic-settings 全局配置
│   │   ├── db.py                    # 数据库引擎、会话、初始化、权限种子
│   │   └── security.py              # JWT 工具、密码哈希
│   ├── deps/                        # FastAPI 依赖注入
│   │   ├── db.py                    # SessionDep 数据库会话依赖
│   │   ├── auth.py                  # CurrentUser、Token 解析
│   │   ├── permission.py            # require_permission RBAC 校验
│   │   └── audit.py                # AuditInfo、log_audit 审计依赖
│   ├── models/
│   │   └── db/
│   │       ├── base.py              # UUIDPrimaryKeyMixin, TimestampMixin
│   │       ├── user.py              # User 模型
│   │       ├── role.py              # Role 模型
│   │       ├── permission.py        # Permission 模型
│   │       ├── user_role.py         # UserRole 关联表
│   │       ├── role_permission.py   # RolePermission 关联表
│   │       ├── audit_log.py         # AuditLog 模型
│   │       ├── system_setting.py    # SystemSetting 模型
│   │       └── upload_file.py       # UploadFile 模型
│   ├── schemas/                     # Pydantic 请求/响应模型
│   │   ├── response.py              # Response[T] 统一响应泛型
│   │   ├── token.py                 # Token 相关 Schema
│   │   ├── user.py                  # 用户 Schema
│   │   ├── role.py                  # 角色 Schema
│   │   ├── permission.py           # 权限 Schema
│   │   ├── audit_log.py            # 审计日志 Schema
│   │   ├── system_setting.py       # 系统设置 Schema
│   │   └── upload.py               # 上传相关 Schema
│   └── services/                    # 业务逻辑层
│       ├── auth_service.py          # 认证服务
│       ├── user_service.py         # 用户服务
│       ├── role_service.py         # 角色服务
│       ├── audit_log_service.py    # 审计日志服务
│       ├── system_setting_service.py # 系统设置服务
│       └── upload_service.py       # 文件上传服务
├── tests/                           # 测试套件
│   ├── conftest.py                 # pytest fixture 配置
│   ├── api/                        # API 路由测试
│   │   └── admin/
│   ├── services/                   # 服务层测试
│   └── deps/                       # 依赖注入测试
├── pyproject.toml                   # uv 依赖管理
└── alembic.ini                     # Alembic 配置
```

### 4.2 分层职责

```
┌─────────────────────────────────────────────────────────────┐
│                      Router Layer (api/routers)             │
│  - 处理 HTTP 协议细节                                        │
│  - 请求参数验证                                               │
│  - 显式返回 Response.ok(data=...)                            │
│  - 依赖注入权限校验                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer (services)                 │
│  - 封装所有业务逻辑                                           │
│  - 事务管理                                                  │
│  - 数据组装与转换                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Model Layer (models/db)                 │
│  - SQLModel ORM 定义                                         │
│  - 表关系映射                                                │
│  - 数据校验                                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database (PostgreSQL)                       │
│  - 数据持久化存储                                             │
│  - 事务控制                                                  │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 数据库模型关系

```
t_user ──(N:N)── t_user_role ──(N:1)── t_role ──(N:N)── t_role_permission ──(N:1)── t_permission
                                                                                     │
                                                                                     ▼
t_audit_log  ──────────────────────────────────────────────────────────────────────► t_user
                                                                                     │
t_system_setting                                                                           │
                                                                                     ▼
t_upload_file ──────────────────────────────────────────────────────────────────────► t_user
```

**核心表说明：**

| 表名 | 模型 | 说明 |
|------|------|------|
| `t_user` | User | 用户账户（邮箱、密码哈希、激活状态） |
| `t_role` | Role | 角色定义（name、code、is_super_role） |
| `t_permission` | Permission | 最小权限单元（resource + action 唯一键） |
| `t_user_role` | UserRole | 用户-角色关联 |
| `t_role_permission` | RolePermission | 角色-权限关联 |
| `t_audit_log` | AuditLog | 操作审计日志（用户、IP、操作类型、详情） |
| `t_system_setting` | SystemSetting | 系统配置（key-value，含公开/私有属性） |
| `t_upload_file` | UploadFile | 上传文件记录（路径、类型、大小、上传人） |

### 4.4 API 路由设计

所有 API 遵循 `/api/v1` 前缀规范：

**公开接口（无需认证）：**
- `POST /api/v1/login/access-token` - JWT 登录
- `GET /api/v1/system-settings/public` - 获取公开系统配置

**用户自服务接口（需登录）：**
- `GET /api/v1/users/me` - 获取当前用户信息
- `PATCH /api/v1/users/me` - 更新个人资料
- `PATCH /api/v1/users/me/password` - 修改密码

**管理端接口（需登录 + 相应权限）：**
- `GET /api/v1/admin/dashboard/stats` - 仪表盘统计
- `GET/POST /api/v1/admin/users` - 用户列表/创建
- `GET/PATCH/DELETE /api/v1/admin/users/{id}` - 用户详情/更新/删除
- `GET /api/v1/admin/roles` - 角色列表
- `POST /api/v1/admin/roles` - 创建角色
- `GET/PATCH/DELETE /api/v1/admin/roles/{id}` - 角色详情/更新/删除
- `GET/PATCH /api/v1/admin/roles/{id}/permissions` - 获取/更新角色权限
- `GET /api/v1/admin/audit-logs` - 审计日志列表
- `GET /api/v1/admin/system-settings` - 获取系统设置
- `PATCH /api/v1/admin/system-settings` - 更新系统设置
- `POST /api/v1/admin/upload` - 文件上传

### 4.5 统一响应结构

```typescript
// 成功响应
{
  "code": 200,
  "message": "success",
  "data": { ... }
}

// 错误响应
{
  "code": 403,
  "message": "权限不足",
  "data": null
}
```

后端路由使用 `Response.ok(data=...)` 显式返回，异常由全局异常处理器统一处理。

### 4.6 认证与安全

**JWT Token 流程：**
1. 用户提交 `email + password` 到 `/login/access-token`
2. 后端验证密码，成功后签发 JWT Access Token
3. 前端将 Token 存储于 `localStorage`
4. 后续请求通过 `Authorization: Bearer <token>` 头部携带
5. 后端 `auth` 依赖解析 Token，注入 `CurrentUser`

**密码安全：**
- 使用 Argon2 + Bcrypt 双重哈希
- 防时序攻击：无论用户是否存在，密码验证耗时一致

### 4.7 初始化流程

应用启动时通过 `lifespan` 钩子自动执行 `init_db()`：

1. 创建内置角色 `superuser`（如不存在）
2. 同步 `BUILTIN_PERMISSIONS` 权限种子数据
3. 创建首个管理员（如 `.env` 中配置）

---

## 5. 前端架构

### 5.1 目录结构

```
frontend/
├── src/
│   ├── main.tsx                     # 根渲染入口
│   ├── App.tsx                      # 全局 Providers
│   ├── router.tsx                   # 集中式路由表
│   ├── globals.css                  # Tailwind 全局样式
│   │
│   ├── components/
│   │   ├── ui/                     # Shadcn/ui 基础组件
│   │   ├── layout/                 # 布局组件
│   │   │   ├── admin-sidebar.tsx   # 管理端侧边栏
│   │   │   ├── admin-topbar.tsx    # 管理端顶部栏
│   │   │   └── admin-layout.tsx   # 管理端布局
│   │   └── shared/                 # 通用业务组件
│   │       ├── confirm-dialog.tsx
│   │       ├── error-boundary.tsx
│   │       └── page-header.tsx
│   │
│   ├── layouts/
│   │   ├── root-layout.tsx         # 根布局（系统环境初始化）
│   │   ├── auth-layout.tsx         # 认证布局（登录页等）
│   │   └── admin-layout.tsx        # 管理端布局（嵌套路由）
│   │
│   ├── pages/
│   │   ├── login.tsx               # 登录页
│   │   ├── not-found.tsx           # 404 页面
│   │   └── admin/                  # 管理端页面
│   │       ├── dashboard.tsx       # 仪表盘
│   │       ├── users/              # 用户管理
│   │       │   ├── list.tsx
│   │       │   └── detail.tsx
│   │       ├── roles.tsx           # 角色管理
│   │       ├── audit-logs.tsx      # 审计日志
│   │       └── system-settings.tsx # 系统设置
│   │
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts           # Fetch 封装（拦截器、Token 注入）
│   │   │   └── endpoints/          # API 接口定义
│   │   ├── auth/
│   │   │   ├── context.tsx         # AuthContext（用户状态）
│   │   │   ├── guard.tsx           # RequireAuth 路由守卫
│   │   │   └── hooks.ts            # useAuth 等认证钩子
│   │   ├── hooks/                  # 业务数据钩子（基于 TanStack Query）
│   │   ├── schemas/               # Zod 验证 Schema
│   │   ├── types/                  # TypeScript 类型声明
│   │   ├── utils/
│   │   │   ├── permission-labels.ts # 权限标签映射
│   │   │   ├── role-labels.ts      # 角色标签映射
│   │   │   └── cn.ts               # className 合并工具
│   │   └── system-settings/        # 系统配置同步逻辑
│   │
│   └── providers/
│       └── theme-provider.tsx       # 主题Provider（light/dark/system）
```

### 5.2 路由架构

采用 React Router v7 集中式路由定义：

```typescript
const router = createBrowserRouter([
  {
    element: <AuthLayout />,
    children: [
      { path: '/login', element: <LoginPage /> },
    ],
  },
  {
    element: <RequireAuth><AdminLayout /></RequireAuth>,
    children: [
      { path: '/', element: <DashboardPage /> },
      { path: '/admin/users', element: <UserListPage /> },
      { path: '/admin/users/:id', element: <UserDetailPage /> },
      { path: '/admin/roles', element: <RolesPage /> },
      { path: '/admin/audit-logs', element: <AuditLogsPage /> },
      { path: '/admin/system-settings', element: <SystemSettingsPage /> },
    ],
  },
  { path: '*', element: <NotFoundPage /> },
]);
```

**RequireAuth 守卫逻辑：**
1. 未登录 → 重定向到 `/login?returnUrl=...`
2. 已登录但无权限 → 重定向到默认页面
3. 加载中 → 显示骨架屏

### 5.3 状态管理

| 状态类型 | 管理方式 | 说明 |
|---------|---------|------|
| 用户认证态 | AuthContext | 登录状态、当前用户信息 |
| 服务端数据 | TanStack Query | 自动缓存、重试、分页 |
| 主题偏好 | ThemeProvider | localStorage + 系统偏好 |
| 系统配置 | SystemSettingsContext | 后端下发的品牌配置 |

### 5.4 API Client

`lib/api/client.ts` 封装基于 `fetch` 的 HTTP 客户端：

- **Token 注入**：自动从 `localStorage` 提取并设置 `Authorization` 头
- **响应解包**：提取后端 `Response.code/data` 中的 `data`
- **401 处理**：检测到未授权，清除本地态并跳转登录页

### 5.5 权限系统集成

前端权限体系与后端 RBAC 完全对齐：

**路由守卫（permissions 参数）：**
```tsx
<RequireAuth permissions={['user:read']}>
  <UserListPage />
</RequireAuth>
```

**侧边栏动态渲染：**
```tsx
const adminNavigation = [
  {
    title: '用户管理',
    url: '/admin/users',
    icon: Users,
    permissions: ['user:read'],
  },
  // 无权限的菜单项自动隐藏
];
```

**权限钩子（组件内判断）：**
```typescript
const { hasPermission } = useAuth();
if (hasPermission('user:delete')) {
  // 渲染删除按钮
}
```

---

## 6. RBAC 权限系统

### 6.1 权限定义

最小管控单元为 `resource:action` 组合：

| resource | action | 权限说明 |
|----------|--------|---------|
| user | create/read/update/delete | 用户管理 |
| role | create/read/update/delete | 角色管理 |
| audit_log | read | 审计日志查看 |
| system_setting | read/update | 系统设置 |
| dashboard | read | 仪表盘 |
| upload | create/read/delete | 文件上传 |

### 6.2 内置角色

| 角色 | 说明 | 权限 |
|------|------|------|
| superuser | 超级管理员 | 拥有所有权限（自动继承） |

### 6.3 权限校验流程

```
请求 → Router (dependencies=[require_permission("user", "read")])
       │
       ▼
   Deps: require_permission("user", "read")
       │
       ├─── 是 superuser？── 是 → 放行
       │
       └─── 否 → 查询用户角色 → 检查角色权限
                    │
                    ├─── 有权限 → 放行
                    │
                    └─── 无权限 → 403 Forbidden
```

---

## 7. 文件结构总览

```
admin-template/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routers/          # API 路由
│   │   ├── core/                  # 核心配置
│   │   ├── deps/                  # 依赖注入
│   │   ├── models/db/            # 数据库模型
│   │   ├── schemas/             # Pydantic 模型
│   │   └── services/            # 业务逻辑
│   ├── tests/
│   ├── alembic/
│   └── docs/                    # 后端文档
├── frontend/
│   ├── src/
│   │   ├── components/          # React 组件
│   │   ├── layouts/             # 布局组件
│   │   ├── pages/               # 页面组件
│   │   ├── lib/                 # 工具与 API
│   │   └── providers/           # Context Providers
│   └── docs/                    # 前端文档
├── docs/                        # 项目文档
│   ├── template-guide.md        # 模板使用指南
│   ├── rbac-extension-guide.md   # RBAC 扩展指南
│   └── architecture.md          # 架构文档
├── docker/
├── .env.example
├── Makefile
├── README.md
└── AGENTS.md
```

---

## 8. 开发工作流

### 8.1 快速启动

**Docker 模式（推荐）：**
```bash
cp .env.example .env
docker compose -f docker/docker-compose.yml up -d --build
```

**本地开发模式：**
```bash
# 安装依赖
cd backend && uv sync
cd frontend && pnpm install

# 启动数据库
docker compose -f docker/docker-compose.yml up -d db

# 数据库迁移
make db-upgrade

# 并发启动
make dev
```

### 8.2 常用命令

| 命令 | 说明 |
|------|------|
| `make dev` | 并发启动前后端开发服务器 |
| `make test` | 运行后端测试 |
| `make lint` | 运行前后端代码检查 |
| `make build-frontend` | 前端生产构建 |
| `make check` | 综合检查（lint + test + build） |
| `make db-revision` | 生成数据库迁移脚本 |
| `make db-upgrade` | 应用数据库迁移 |

### 8.3 新增业务模块

详见 [RBAC 扩扩展指南](./rbac-extension-guide.md)。

标准流程：
1. 后端 `db.py` 声明权限种子
2. 后端 `models/db/` 创建模型
3. 后端 `schemas/` 创建 Schema
4. 运行 `make db-revision` 生成迁移
5. 后端 `api/routers/` 编写接口（依赖 `require_permission`）
6. 后端 `services/` 编写业务逻辑
7. 前端 `lib/utils/permission-labels.ts` 补充标签
8. 前端 `pages/` 创建页面组件
9. 前端 `router.tsx` 注册路由
10. 前端 `components/layout/admin-sidebar.tsx` 添加菜单
11. 编写测试用例

---

## 9. 安全注意事项

- `.env` 文件不提交到版本控制
- 上传文件验证扩展名、MIME 类型、文件签名、大小
- 敏感操作记录审计日志
- 不在数据库中存储云服务商密钥
- JWT Secret 使用强随机密钥
- 密码使用 Argon2 + Bcrypt 哈希
