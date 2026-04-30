# NOS Agent Carrier (Admin Boilerplate)

开箱即用的企业级现代中后台管理底座（Admin Boilerplate），采用全栈最优实践构建，专为二次开发和快速业务迭代设计。

## 🚀 核心技术栈

- **后端**: FastAPI + SQLModel + PostgreSQL (基于 `uv` 管理)
- **前端**: React 19 + Vite + Tailwind CSS v4 + Shadcn/ui (基于 `pnpm` 管理)
- **容器化**: Docker + Docker Compose

## ✨ 核心特性

- **纯净版底座**：彻底剥离具体业务逻辑，只保留所有后台系统都需要的**基础设施**。
- **现代化认证**：基于 JWT (OAuth2 规范) 的登录认证与自服务（修改资料、修改密码）。
- **细粒度 RBAC**：基于资源与操作的权限控制，抛弃硬编码，后台完全可控角色及权限。
- **动态系统设置**：前端 UI 不硬编码 Logo、系统名称、Favicon，全盘由后台设置接口动态下发。
- **文件上传服务**：内置基于本地存储的静态文件上传逻辑及安全大小控制。
- **代码质量**：后端强制 Ruff / Pytest；前端强类型 Strict TypeScript + ESLint。

## 📦 快速开始 (Quick Start)

### 选项 A：使用 Docker 极速体验 (推荐)
```bash
cp .env.example .env
# 编辑 .env 修改密码等参数
docker-compose -f docker/docker-compose.yml up -d --build
```
> 前端将运行在 `http://localhost:5173`，后端 API 运行在 `http://localhost:8000`。

### 选项 B：本地原生开发
1. **环境准备**：安装 [Node.js 18+](https://nodejs.org/)、[pnpm](https://pnpm.io/)、[uv](https://docs.astral.sh/uv/) 和 PostgreSQL 数据库。
2. **环境变量**：`cp .env.example .env` 并配置 `POSTGRES_PASSWORD`。
3. **启动数据库**（可使用 docker 仅启动数据库）：`docker-compose -f docker/docker-compose.yml up -d db`
4. **数据库初始化与迁移**：
   ```bash
   make db-upgrade
   ```
5. **并发启动前后端**：
   ```bash
   make dev
   ```

系统启动后，访问 `http://localhost:5173`。首次启动会自动在数据库创建 `admin@example.com`（密码见 `.env` 中的 `FIRST_SUPERUSER_PASSWORD`），请使用该账号登录。

## 📖 开发者指南

- **项目架构与原理**：参阅 [Backend Architecture](./backend/docs/architecture.md) 与 [Frontend Architecture](./frontend/docs/architecture-frontend.md)。
- **如何增加新业务模块**：参阅 [RBAC 扩展指南](./docs/rbac-extension-guide.md)。
- **本地运维与开发命令**：本项目提供根目录的 `Makefile`，常用命令：
  - `make lint`: 运行全栈代码质量检查。
  - `make test`: 运行全栈自动化测试。
  - `make db-revision`: 为后端修改的模型生成 Alembic 迁移脚本。

## 📄 协议
MIT License
