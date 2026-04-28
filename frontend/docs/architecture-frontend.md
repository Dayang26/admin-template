# 前端架构设计

> 日期：2026-04-27
> 状态：重构中（从 Next.js 迁移至 Vite + React SPA）

---

## 1. 技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| 构建工具 | Vite | 快速开发服务器 + 生产构建 |
| 框架 | React 19 | SPA，纯客户端渲染 |
| 语言 | TypeScript | strict mode |
| 路由 | React Router v7 | 客户端路由，支持嵌套布局 |
| UI 组件库 | Shadcn/ui | 基于 Radix UI + Tailwind CSS |
| 样式 | Tailwind CSS v4 | Shadcn/ui 依赖 |
| 数据请求 | TanStack Query (React Query) | 缓存、自动重试、分页支持 |
| 状态管理 | React Context | 仅用于 Auth 全局状态 |
| 主题 | 自定义 ThemeProvider | 暗色/亮色切换（基于 CSS 变量 + localStorage） |
| 表单 | React Hook Form + Zod | Shadcn/ui 推荐搭配 |
| 图标 | Lucide React | Shadcn/ui 内置图标库 |
| HTTP 客户端 | fetch (原生) | 封装统一拦截器 |
| 测试 | Vitest + React Testing Library | 单元测试 + 组件测试 |
| E2E 测试 | Playwright | 端到端测试 |

---

## 1.1 开发规范与最佳实践

- **组件库 API 统一**：项目同时依赖 Radix UI（Shadcn/ui 底层）和 `@base-ui/react`。两者有各自的组合模式：
  - Radix UI 使用 `asChild` prop。
  - `@base-ui/react` 使用 `render=` prop。
  - **严禁混用**：不得在同一组件上同时使用 `asChild` 和 `render=`。
  - **推荐做法**：在 Shadcn Sidebar 等基于 `@base-ui/react` 的组件树中，统一使用 `render=` 模式进行组合。
- **路由组织**：使用 React Router v7 的嵌套路由 + `<Outlet />` 实现布局复用，避免在每个页面重复布局代码。
- **懒加载**：所有页面组件使用 `React.lazy()` + `<Suspense>` 实现按需加载，减小首屏体积。

---

## 2. 目录结构

```
frontend/
├── public/                           # 静态资源
│   └── favicon.ico
├── src/
│   ├── main.tsx                      # 应用入口（挂载 React）
│   ├── App.tsx                       # 根组件（Providers + Router）
│   ├── router.tsx                    # 路由配置（集中定义）
│   ├── globals.css                   # Tailwind + Shadcn 全局样式
│   │
│   ├── components/
│   │   ├── ui/                       # Shadcn/ui 组件（CLI 自动生成）
│   │   ├── layout/
│   │   │   ├── admin-sidebar.tsx     # 管理端侧边栏（角色动态菜单）
│   │   │   ├── admin-topbar.tsx      # 管理端顶栏
│   │   │   ├── student-header.tsx    # 学生端顶栏
│   │   │   ├── user-menu.tsx         # 用户头像下拉菜单
│   │   │   └── theme-toggle.tsx      # 主题切换按钮
│   │   └── shared/
│   │       ├── data-table.tsx        # 通用数据表格（分页 + 排序）
│   │       ├── confirm-dialog.tsx    # 确认弹窗（删除等危险操作）
│   │       ├── page-header.tsx       # 页面标题 + 面包屑
│   │       ├── loading-skeleton.tsx  # 骨架屏加载态
│   │       └── error-boundary.tsx    # 全局错误边界
│   │
│   ├── layouts/
│   │   ├── auth-layout.tsx           # 认证页布局（全屏居中，无侧边栏）
│   │   ├── admin-layout.tsx          # 管理端布局（Sidebar + Topbar + Content）
│   │   └── student-layout.tsx        # 学生端布局（Header + Content）
│   │
│   ├── pages/
│   │   ├── login.tsx                 # 统一登录页
│   │   ├── not-found.tsx             # 404 页面
│   │   │
│   │   ├── student/
│   │   │   ├── home.tsx              # 学生首页
│   │   │   └── profile.tsx           # 个人中心
│   │   │
│   │   └── admin/
│   │       ├── dashboard.tsx         # Dashboard 总览
│   │       ├── users/
│   │       │   ├── list.tsx          # 用户列表
│   │       │   ├── create.tsx        # 创建用户
│   │       │   └── detail.tsx        # 用户详情/编辑
│   │       ├── classes/
│   │       │   ├── list.tsx          # 班级列表
│   │       │   ├── create.tsx        # 创建班级
│   │       │   └── detail.tsx        # 班级详情 + 成员管理
│   │       └── my-classes/
│   │           ├── list.tsx          # 我的班级列表（教师）
│   │           └── detail.tsx        # 班级成员查看（教师）
│   │
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts            # fetch 封装（token 注入、统一响应解析、401 处理）
│   │   │   ├── auth.ts              # 登录接口
│   │   │   ├── users.ts             # 用户相关接口
│   │   │   ├── classes.ts           # 班级相关接口
│   │   │   ├── teacher.ts           # 教师相关接口
│   │   │   └── dashboard.ts         # Dashboard 接口
│   │   ├── auth/
│   │   │   ├── context.tsx          # AuthProvider + useAuth Hook
│   │   │   └── guard.tsx            # 路由守卫组件（RoleGuard）
│   │   ├── hooks/
│   │   │   ├── use-users.ts         # 用户数据 hooks (TanStack Query)
│   │   │   ├── use-classes.ts       # 班级数据 hooks
│   │   │   └── use-dashboard.ts     # Dashboard 数据 hooks
│   │   ├── schemas/
│   │   │   └── login.ts             # 登录表单 Zod schema
│   │   ├── types/
│   │   │   ├── api.ts               # ApiResponse<T> 等通用类型
│   │   │   ├── user.ts              # User 相关类型
│   │   │   ├── class.ts             # Class 相关类型
│   │   │   └── dashboard.ts         # Dashboard 相关类型
│   │   └── utils/
│   │       └── cn.ts                # Tailwind class merge 工具
│   │
│   └── providers/
│       └── index.tsx                 # 全局 Providers 组合（Theme + QueryClient + Auth + Toaster）
│
├── index.html                        # Vite 入口 HTML
├── vite.config.ts                    # Vite 配置（含 API 代理）
├── tailwind.config.ts                # Tailwind CSS 配置
├── tsconfig.json                     # TypeScript 配置
├── tsconfig.app.json                 # 应用 TS 配置
├── tsconfig.node.json                # Node 端 TS 配置（Vite 配置文件用）
├── components.json                   # Shadcn/ui 配置
├── eslint.config.js                  # ESLint 配置
├── vitest.config.ts                  # Vitest 测试配置
├── playwright.config.ts              # Playwright E2E 配置
└── package.json
```

---

## 3. 路由设计

### 3.1 路由配置方式

使用 React Router v7 的 `createBrowserRouter` + `RouterProvider` 模式，在 `src/router.tsx` 中集中定义所有路由。通过嵌套路由实现布局复用：

```tsx
// src/router.tsx 结构示意
const router = createBrowserRouter([
  // 认证路由（AuthLayout）
  {
    element: <AuthLayout />,
    children: [
      { path: '/login', element: <LoginPage /> },
    ],
  },
  // 学生端路由（StudentLayout + 需要登录）
  {
    element: <RequireAuth><StudentLayout /></RequireAuth>,
    children: [
      { path: '/', element: <StudentHome /> },
      { path: '/profile', element: <ProfilePage /> },
    ],
  },
  // 管理端路由（AdminLayout + 需要 teacher/superuser 角色）
  {
    element: <RequireAuth roles={['teacher', 'superuser']}><AdminLayout /></RequireAuth>,
    children: [
      { path: '/admin', element: <DashboardPage /> },
      { path: '/admin/users', element: <UserListPage /> },
      { path: '/admin/users/create', element: <UserCreatePage /> },
      { path: '/admin/users/:id', element: <UserDetailPage /> },
      { path: '/admin/classes', element: <ClassListPage /> },
      { path: '/admin/classes/create', element: <ClassCreatePage /> },
      { path: '/admin/classes/:id', element: <ClassDetailPage /> },
      { path: '/admin/my-classes', element: <MyClassListPage /> },
      { path: '/admin/my-classes/:id', element: <MyClassDetailPage /> },
    ],
  },
  // 404
  { path: '*', element: <NotFoundPage /> },
]);
```

### 3.2 路由表

| 路径 | 页面 | 可访问角色 | 布局 |
|------|------|-----------|------|
| `/login` | 统一登录页 | 未认证用户 | Auth Layout（全屏居中） |
| `/` | 学生首页 | student | Student Layout |
| `/profile` | 个人中心 | student | Student Layout |
| `/admin` | 管理端首页 | teacher, superuser | Admin Layout |
| `/admin/users` | 用户列表 | superuser | Admin Layout |
| `/admin/users/create` | 创建用户 | superuser | Admin Layout |
| `/admin/users/:id` | 用户详情/编辑 | superuser | Admin Layout |
| `/admin/classes` | 班级列表 | superuser | Admin Layout |
| `/admin/classes/create` | 创建班级 | superuser | Admin Layout |
| `/admin/classes/:id` | 班级详情+成员管理 | superuser | Admin Layout |
| `/admin/my-classes` | 我的班级 | teacher | Admin Layout |
| `/admin/my-classes/:id` | 班级成员查看 | teacher | Admin Layout |

### 3.3 登录后跳转逻辑

```
登录成功
  │
  ├── 角色包含 student → 跳转 /
  └── 角色包含 teacher 或 superuser → 跳转 /admin
```

### 3.4 路由守卫逻辑

纯客户端 SPA 模式，路由守卫完全在客户端实现：

```
RequireAuth 组件（包裹需要登录的路由）
  │
  ├── AuthContext.isLoading → 显示全屏 Loading
  ├── 无 token / 无 user → 重定向到 /login（携带 returnUrl）
  └── 已登录
      │
      ├── 指定了 roles 参数 → 检查用户角色是否匹配
      │   ├── 匹配 → 渲染子路由 <Outlet />
      │   └── 不匹配 → 重定向到对应默认页
      └── 未指定 roles → 直接渲染子路由

登录页守卫（AuthLayout 内）
  │
  ├── 已登录 → 根据角色重定向到 / 或 /admin
  └── 未登录 → 渲染登录表单
```

---

## 4. 布局架构

### 4.1 学生端布局 (Student Layout)

```
┌──────────────────────────────────────────┐
│  Header                                  │
│  [Logo]           [用户名 ▼] [🌙/☀️]     │
├──────────────────────────────────────────┤
│                                          │
│              Content Area                │
│           (简洁卡片式布局)                 │
│            <Outlet />                    │
│                                          │
└──────────────────────────────────────────┘
```

- 顶部 Header：Logo + 用户名下拉菜单（个人中心、退出登录）+ 主题切换
- 主体区域：居中内容区，最大宽度限制，卡片式布局
- 使用 `<Outlet />` 渲染子路由页面

### 4.2 管理端布局 (Admin Layout)

```
┌──────┬───────────────────────────────────┐
│      │  Topbar          [用户名 ▼] [🌙] │
│ Side ├───────────────────────────────────┤
│ bar  │                                   │
│      │           Content Area            │
│ 动态  │         (数据表格/表单)            │
│ 菜单  │          <Outlet />               │
│      │                                   │
└──────┴───────────────────────────────────┘
```

- 左侧 Sidebar：可折叠，菜单根据角色动态渲染
- 顶部 Topbar：面包屑 + 用户下拉菜单 + 主题切换
- 主体区域：自适应宽度，使用 `<Outlet />` 渲染子路由页面

### 4.3 角色动态菜单

**Superuser 菜单：**
```
📊 Dashboard
👥 用户管理
🏫 班级管理
```

**Teacher 菜单：**
```
📚 我的班级
```

---

## 5. 认证与授权

### 5.1 Token 存储策略

| 存储位置 | 用途 |
|---------|------|
| localStorage (`token`) | 持久化存储，页面刷新后恢复登录状态 |
| 内存 (AuthContext) | 客户端 API 调用时携带 |

> 注：纯 SPA 模式下不再需要 Cookie 存储（没有服务端中间件需要读取 token）。

### 5.2 AuthContext 设计

```typescript
interface AuthContextType {
  user: UserDetail | null        // 当前用户信息（含角色、班级）
  token: string | null
  isLoading: boolean             // 初始化加载中
  login: (token: string) => Promise<UserDetail | undefined>
  logout: () => void
  // 计算属性
  isStudent: boolean
  isTeacher: boolean
  isSuperuser: boolean
}
```

### 5.3 初始化流程

```
App 启动
  │
  ├── 从 localStorage 读取 token
  ├── 若有 token → 调用 GET /api/v1/users/me 获取用户信息
  │   ├── 成功 → 设置 user + token 到 Context
  │   └── 401 → 清除 token，等待路由守卫重定向到 /login
  └── 若无 token → isLoading=false，等待路由守卫处理
```

### 5.4 RequireAuth 组件

```typescript
// 用法：在路由配置中包裹需要认证的布局
<RequireAuth roles={['superuser']}>
  <AdminLayout />
</RequireAuth>
```

功能：
- 检查登录状态，未登录重定向到 `/login?returnUrl=当前路径`
- 可选 `roles` 参数，检查用户角色是否匹配
- 加载中显示全屏 Loading Spinner

---

## 6. API 层设计

### 6.1 API 代理（开发环境）

Vite 开发服务器配置代理，将 `/api` 请求转发到后端：

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

生产环境通过 Nginx 或其他反向代理实现同样效果。

### 6.2 统一客户端 (client.ts)

```typescript
// 核心能力：
// 1. 自动从 localStorage 读取 token，注入 Authorization: Bearer <token>
// 2. 解析统一响应结构 { code, message, data }
// 3. code !== 2xx 时抛出 ApiError（携带 code 和 message）
// 4. 401 时自动清除 token 并跳转 /login

async function apiClient<T>(url: string, options?: RequestInit): Promise<T>
```

### 6.3 API 模块划分

| 模块 | 文件 | 接口 |
|------|------|------|
| 认证 | `auth.ts` | login |
| 用户 (admin) | `users.ts` | list, get, create, update, delete |
| 班级 (admin) | `classes.ts` | list, get, create, update, delete, members CRUD |
| 教师 | `teacher.ts` | myClasses, classMembers |
| 用户自服务 | `me.ts` | getMe, updateMe, changePassword |
| Dashboard | `dashboard.ts` | getStats |

### 6.4 TanStack Query Hooks

每个 API 模块对应一组 hooks，提供缓存和自动刷新：

```typescript
// 示例
function useUsers(params: UserSearchParams) {
  return useQuery({ queryKey: ['users', params], queryFn: () => getUsers(params) })
}

function useDeleteUser() {
  return useMutation({
    mutationFn: deleteUser,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] })
  })
}
```

---

## 7. 类型定义

与后端 Schema 一一对应：

```typescript
// api.ts — 统一响应
interface ApiResponse<T> {
  code: number
  message: string
  data: T | null
}

interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// user.ts
interface UserPublic {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  created_at: string
}

interface ClassMembership {
  class_id: string
  class_name: string
  role: string
}

interface UserDetail extends UserPublic {
  roles: string[]
  class_memberships: ClassMembership[]
}

// class.ts
interface ClassPublic {
  id: string
  name: string
  description: string | null
  created_at: string
  updated_at: string
}

interface ClassMember {
  user_id: string
  email: string
  full_name: string | null
  role: string
  joined_at: string
}

// dashboard.ts
interface DashboardStats {
  total_users: number
  active_users: number
  total_classes: number
  role_distribution: Record<string, number>
}
```

---

## 8. 页面功能清单

### 8.1 登录页 (`/login`)

- 邮箱 + 密码表单
- 表单校验（React Hook Form + Zod）
- 登录成功后根据角色跳转
- 已登录用户自动重定向
- 错误提示（Toast）

### 8.2 学生首页 (`/`)

- 暂空白，显示欢迎语

### 8.3 个人中心 (`/profile`)

- 信息展示卡片（邮箱、姓名、角色、班级）
- 编辑姓名表单
- 修改密码表单（旧密码 + 新密码）

### 8.4 管理端 Dashboard (`/admin`)

- **Superuser**：统计卡片（用户总数、活跃用户、班级总数）+ 角色分布
- **Teacher**：重定向到 `/admin/my-classes`

### 8.5 用户管理 (`/admin/users`)

- DataTable：邮箱、姓名、角色、状态、创建时间
- 搜索栏：邮箱/姓名模糊搜索、角色下拉筛选
- 操作：查看详情、编辑、删除（确认弹窗）、创建
- 分页

### 8.6 用户详情 (`/admin/users/:id`)

- 用户信息卡片
- 编辑表单（姓名、密码、激活状态、角色）
- 班级成员身份列表

### 8.7 班级管理 (`/admin/classes`)

- DataTable：名称、描述、创建时间
- 搜索栏：名称模糊搜索
- 操作：查看详情、编辑、删除、创建
- 分页

### 8.8 班级详情 (`/admin/classes/:id`)

- 班级信息卡片 + 编辑表单
- 成员列表 Tab（DataTable）
- 添加成员弹窗（选择用户 + 指定角色）
- 移除成员（确认弹窗）

### 8.9 我的班级 - 教师 (`/admin/my-classes`)

- 班级卡片列表（名称、描述）
- 点击进入成员查看

### 8.10 班级成员 - 教师 (`/admin/my-classes/:id`)

- 只读成员列表（姓名、邮箱、角色）
- 无增删操作

---

## 9. 主题系统

使用自定义 ThemeProvider 实现暗色/亮色切换：

- 通过在 `<html>` 元素上切换 `class="dark"` 实现
- Shadcn/ui 原生支持 CSS 变量切换
- 主题状态持久化到 localStorage
- 顶栏提供切换按钮（太阳/月亮图标）
- 支持 system / light / dark 三种模式

---

## 10. 构建与部署

### 10.1 开发环境

```bash
cd frontend
npm install
npm run dev          # 启动 Vite 开发服务器（默认 http://localhost:5173）
```

Vite 开发服务器自动代理 `/api` 请求到后端 `http://localhost:8000`。

### 10.2 生产构建

```bash
npm run build        # 输出到 dist/
npm run preview      # 本地预览生产构建
```

### 10.3 生产部署

SPA 模式需要配置 Web 服务器（如 Nginx）：
- 所有非静态资源请求 fallback 到 `index.html`（支持客户端路由）
- `/api/*` 请求反向代理到后端服务

```nginx
# Nginx 配置示例
server {
    listen 80;
    root /path/to/frontend/dist;

    location /api/ {
        proxy_pass http://backend:8000;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 11. TODO 清单

### Phase 0：项目初始化
- [x] 使用 Vite 创建 React + TypeScript 项目
- [x] 安装并配置 Shadcn/ui（Vite 模式）
- [x] 安装 React Router v7、TanStack Query、React Hook Form、Zod、Sonner
- [x] 配置 Vite API 代理（server.proxy → 后端）
- [x] 配置路径别名（`@/` → `src/`）
- [x] 搭建目录骨架

### Phase 1：基础设施
- [x] 实现 `lib/api/client.ts`（统一 fetch 封装）
- [x] 实现 `lib/types/`（所有类型定义）
- [x] 实现 `lib/auth/context.tsx`（AuthProvider）
- [x] 实现 `lib/auth/guard.tsx`（RequireAuth 路由守卫）
- [x] 实现 `providers/index.tsx`（全局 Providers 组合）
- [x] 实现 `router.tsx`（路由配置）
- [x] 实现主题切换（ThemeProvider）

### Phase 2：登录页
- [x] 实现登录页 UI + 表单验证
- [x] 实现登录逻辑 + 角色跳转

### Phase 3：管理端布局
- [x] 实现 Admin Sidebar（角色动态菜单）
- [x] 实现 Admin Topbar（面包屑 + 主题切换）
- [x] 实现 Admin Layout（Sidebar + Topbar + Outlet）

### Phase 4：管理端核心页面
- [x] Dashboard 页面（统计卡片）
- [x] 用户列表页（DataTable + 搜索 + 分页）
- [x] 用户详情/编辑页
- [x] 创建用户页
- [x] 班级列表页
- [x] 班级详情页 + 成员管理
- [x] 创建班级页

### Phase 5：教师视角
- [x] 我的班级列表页
- [x] 班级成员查看页

### Phase 6：学生端
- [x] Student Layout（Header + 导航 + 主题切换 + 用户菜单）
- [x] 学生首页（欢迎卡片 + 班级展示）
- [x] 个人中心页（基本信息查看 + 编辑姓名 + 修改密码）

### Phase 7：收尾
- [x] 全局错误边界（ErrorBoundary 组件）
- [x] 路由级错误处理（RouteErrorPage + errorElement）
- [x] 响应式适配（移动端 Sidebar Sheet 模式 + 学生端导航图标模式）
- [x] 404 页面（角色智能跳转）
- [x] 路由守卫验证（学生/管理端角色隔离）
