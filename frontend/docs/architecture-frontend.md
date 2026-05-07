# 前端架构设计 (Admin Boilerplate)

> 项目状态：现代化 React SPA 模版
> 日期：2026-04-29

---

## 1. 技术栈概览

| 类别 | 技术 | 说明 |
|------|------|------|
| 构建工具 | Vite | 快速开发服务器 + 生产构建 |
| 框架 | React 19 | SPA，纯客户端渲染 |
| 语言 | TypeScript | Strict Mode |
| 路由 | React Router v7 | 客户端路由，支持嵌套布局 |
| UI 组件库 | Shadcn/ui | 基于 Radix UI + Tailwind CSS |
| 样式 | Tailwind CSS v4 | 原子化 CSS |
| 数据请求 | TanStack Query (React Query) | 智能缓存、自动重试、分页支持 |
| 状态管理 | React Context | 仅用于 Auth 及系统级基础配置 |
| 主题 | ThemeProvider | 基于 localStorage 和系统偏好控制 light/dark/system |
| 表单 | React Hook Form + Zod | 高性能与强类型校验 |
| HTTP 客户端 | fetch (原生) | 封装统一拦截器 (API Client) |

---

## 2. 核心架构与目录规划

采用领域分离和强复用的组织方式：

```text
frontend/
├── src/
│   ├── main.tsx                      # 根渲染入口
│   ├── App.tsx                       # 全局 Providers 层
│   ├── router.tsx                    # 集中式路由表
│   ├── globals.css                   # 全局样式
│   │
│   ├── components/                   # UI 组件体系
│   │   ├── ui/                       # 基础组件 (通过 Shadcn 自动引入)
│   │   ├── layout/                   # 布局组件 (Sidebar, Topbar, UserMenu)
│   │   └── shared/                   # 通用业务组件 (ConfirmDialog, ErrorBoundary, PageHeader)
│   │
│   ├── layouts/                      # 布局插槽
│   │   ├── root-layout.tsx           # 最外层根布局 (挂载系统环境)
│   │   ├── auth-layout.tsx           # 认证/全屏页布局
│   │   └── admin-layout.tsx          # 管理端标准布局 (后台框架)
│   │
│   ├── pages/                        # 路由页面 (按域划分)
│   │   ├── login.tsx                 # 登录页
│   │   └── admin/                    # 后台管理页面域
│   │       ├── dashboard.tsx         # 数据总览
│   │       ├── users/                # 用户增删改查
│   │       ├── roles.tsx             # 角色查看
│   │       ├── audit-logs.tsx        # 审计日志
│   │       └── system-settings.tsx   # 全局系统设置
│   │
│   ├── lib/                          # 核心业务逻辑与工具
│   │   ├── api/                      # Fetch 客户端封装与接口声明
│   │   ├── auth/                     # 鉴权中心 (Context + Guard)
│   │   ├── hooks/                    # 基于 React Query 的数据 Hook
│   │   ├── schemas/                  # Zod 数据验证约束
│   │   ├── types/                    # 全局 TypeScript 类型声明
│   │   ├── system-settings/          # 动态标题、Logo、配置同步相关逻辑
│   │   └── utils/                    # 通用函数 (如 cn)
│   │
│   └── providers/                    # 全局上下文供给侧
│       └── theme-provider.tsx        # 主题管理
```

---

## 3. 路由与权限架构

### 3.1 集中式路由定义
所有路由都在 `src/router.tsx` 中定义，基于嵌套布局实现无缝的页面切换体验。

```tsx
const router = createBrowserRouter([
  {
    element: <AuthLayout />,
    children: [ { path: '/login', element: <LoginPage /> } ],
  },
  {
    // 全局路由守卫
    element: <RequireAuth><AdminLayout /></RequireAuth>,
    children: [
      { path: '/', element: <DashboardPage /> },
      { path: '/admin/users', element: <UserListPage /> },
      // ... 其它后台页面
    ],
  },
  { path: '*', element: <NotFoundPage /> },
]);
```

### 3.2 RequireAuth 路由守卫
前端在路由跃迁前，执行鉴权校验：
- **未登录**：重定向回 `/login?returnUrl=...`，携带当前页面 URL 作为返回来源。
- **已登录但权限不足**：通过 `permissions` 参数校验，权限不足时重定向至 `getDefaultRoute(user)`。
- **加载态**：当系统处于 API 获取登录状态的过程中，展示全局骨架屏防跳闪。

---

## 4. API 模块与数据层

### 4.1 通用 API Client
在 `lib/api/client.ts` 中封装了基于 `fetch` 的基础客户端：
- **Token 注入**：每次请求拦截提取 `localStorage` 中的 Token。
- **响应解包**：将后端的 `{ code, message, data }` 剥离，抛出纯粹的 `data` 业务层级数据。
- **401 自动驱逐**：如果检测到鉴权失效，立刻清理本地态并推向登录页。

### 4.2 TanStack Query
所有服务通过 React Query 接管状态：
```tsx
// 示例: hook 层封装
export function useUsers(params: UserSearchParams) {
  return useQuery({ queryKey: ['users', params], queryFn: () => getUsers(params) })
}
```
极大简化了加载态 (`isLoading`)、错误态 (`isError`) 和分页数据的同步复杂度。

---

## 5. UI 与布局系统 (AdminLayout)

作为后台模板，页面呈现高度的统一性：

### 整体架构
采用自适应的 Flexbox 模型布局，配合 Shadcn 的 `SidebarProvider` 实现：
- **Sidebar**：左侧动态导航栏，支持根据视口缩小折叠，适配移动端的抽屉式唤起。
- **Topbar**：挂载全局面包屑、动态标题与系统工具栏（头像、退出登录）。
- **Main Content**：利用 `React Router` 的 `<Outlet>` 做无刷新的子页面动态装载。

### 系统设置动态联动
模板避免了臃肿繁杂的“界面过度配置”，而是通过 `SystemSettingsContext` 从接口轻量拉取核心业务设定（如：系统名称、系统 Logo）。
- `ThemeProvider` 基于 `localStorage` 本地偏好和系统 `prefers-color-scheme` 控制 light/dark/system 主题。
- `Document Title` 自动跟随系统的设定进行响应式更改。

---

## 6. 核心业务页面

### 6.1 数据大盘 (Dashboard)
整合 `react-countup` 等动效库，呈现系统概览数据，并在无权限时自动降级展现保护界面。

### 6.2 用户与权限管理 (User/Role/Audit Logs)
- **用户管理**：提供用户 CRUD、多维搜索、角色分配等完整管理功能。
- **角色管理**：提供角色 CRUD、权限绑定等管理功能。
- **Audit Logs**：作为风控页展示系统内的审计追踪日志。

---

## 7. 构建与工程化

### 环境对接
开发环境中通过 Vite 自带的 Proxy 完全抹平前后端跨域壁垒：
```ts
export default defineConfig({
  server: {
    proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } }
  }
})
```

### 部署规范
生产环境下打包输出纯静态资产至 `dist`。配置 Nginx 时仅需将非命中资源指向 `index.html` 即可完成前端路由的无缝回退支持。
