# 前端开发指南 (Manual Setup)

本文档旨在指导开发者如何手动配置并启动前端服务。

## 1. 准备工作

在开始之前，请确保您的开发环境已安装以下工具：

- **Node.js**: 版本 >= 18.x (推荐 20.x 或更高)
- **pnpm**: 推荐使用包管理工具 pnpm (版本 >= 8.x)

## 2. 安装依赖

在 `frontend` 目录下执行：

```bash
cd frontend
pnpm install
```

## 3. 开发环境运行

启动 Vite 开发服务器：

```bash
pnpm dev
```

启动后，您可以访问：
- **本地开发地址**: [http://localhost:5173/](http://localhost:5173/)

### 后端联调 (Proxy)
Vite 已配置自动代理。开发环境下，所有以 `/api` 或 `/uploads` 开头的请求都会被转发到 `http://localhost:8000`。请确保您的后端服务已启动。

## 4. 生产构建

构建静态资源：

```bash
pnpm build
```

构建产物将输出到 `dist/` 目录。

## 5. 代码质量

### 代码检查 (Linting)
```bash
pnpm lint
```

## 6. 常用 Makefile 命令 (推荐)

如果您在根目录下，可以使用项目提供的 `Makefile` 快速操作：

- `make dev-frontend`: 启动前端开发服务器
- `make build-frontend`: 执行前端生产构建
- `make lint-frontend`: 运行前端代码检查
