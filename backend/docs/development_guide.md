# 后端开发指南 (Manual Setup)

本文档旨在指导开发者如何手动配置并启动后端服务。

## 1. 准备工作

在开始之前，请确保您的开发环境已安装以下工具：

- **Python**: 版本 >= 3.12 (推荐使用最新的 3.12.x)
- **PostgreSQL**: 正在运行的数据库实例
- **uv**: 高性能 Python 包管理工具（[安装指南](https://docs.astral.sh/uv/getting-started/installation/)）

## 2. 环境变量配置

项目使用 `.env` 文件管理配置。

1. 在项目根目录下，将 `.env.example` 复制为 `.env`：
   ```bash
   cp .env.example .env
   ```
2. 编辑 `.env` 文件，根据您的本地环境修改以下关键配置：
   - `POSTGRES_PASSWORD`: 您的数据库密码
   - `POSTGRES_DB`: 您的数据库名称 (请先在 PostgreSQL 中手动创建该数据库)
   - `FIRST_SUPERUSER_PASSWORD`: 初始超级管理员的密码 (至少 8 位)
   - `SECRET_KEY`: 运行 `openssl rand -hex 32` 生成一个随机密钥

## 3. 安装依赖

使用 `uv` 自动创建虚拟环境并同步所有依赖：

```bash
cd backend
uv sync
```

## 4. 数据库迁移与初始化

本项目使用 **Alembic** 管理数据库迁移。在首次启动前，需要将表结构应用到数据库中：

```bash
# 在 backend 目录下执行
uv run alembic -c app/alembic.ini upgrade head
```

> [!NOTE]
> 系统在启动时会通过 `lifespan` 钩子自动运行 `init_db()`。
> 这将自动创建默认权限点、超级管理员账号以及系统基础设置。

## 5. 启动后端服务

### 开发模式 (热重载)

使用 `uvicorn` 启动服务，默认监听 `8000` 端口：

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后，您可以访问：
- **API 根路径**: [http://localhost:8000/](http://localhost:8000/)
- **交互式文档 (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 6. 代码质量与测试

### 运行单元测试
```bash
uv run pytest tests/
```

### 代码检查 (Linting)
```bash
uv run ruff check .
```

## 7. 常用 Makefile 命令 (推荐)

如果您在根目录下，可以使用项目提供的 `Makefile` 快速操作：

- `make dev-backend`: 启动后端开发服务器
- `make db-upgrade`: 执行数据库迁移
- `make test-backend`: 运行后端测试
- `make lint-backend`: 运行代码检查
