# Admin Boilerplate - Frontend

基于 Vite + React 19 + TypeScript + Shadcn/ui 的现代化中后台管理模版前端。

## 技术栈
- **框架**: React 19 (SPA 客户端渲染)
- **构建工具**: Vite
- **语言**: TypeScript (Strict Mode)
- **路由**: React Router v7
- **UI 库**: Shadcn/ui (Radix UI + Tailwind CSS)
- **数据请求**: TanStack Query (React Query)
- **表单方案**: React Hook Form + Zod

## 快速开始

### 1. 环境要求
- Node.js 18+
- pnpm 8+ (推荐)

### 2. 安装依赖
```bash
pnpm install
```

### 3. 开发环境运行
```bash
pnpm dev
```
- 本地服务器默认运行在 `http://localhost:5173`。
- Vite 已配置自动 Proxy：所有 `/api` 开头的请求将被直接代理到后端的 `http://localhost:8000`，无需额外配置 CORS 即可联调。

### 4. 生产构建
```bash
pnpm build
```
静态资源将被输出到 `dist/` 目录。在使用 Nginx 等 Web 服务器部署时，请确保所有未匹配路由 fallback 回 `index.html`（以支持客户端路由）。

## 开发与规范
- **组件库**: UI 组件位于 `src/components/ui`（由 Shadcn CLI 管理）。自定义业务组件位于 `src/components/shared` 和 `src/components/layout`。
- **状态管理**: 仅针对用户认证（`lib/auth`）和全局配置（`lib/system-settings`）使用 React Context，其余请求均由 TanStack Query 托管以自动管理缓存。
- **代码规范**: 请遵循 `pnpm lint` 的校验，项目已接入 React Hooks 和 React Compiler 相关的 ESLint 校验规则。
