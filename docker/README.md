# Docker 运维指南

本文档面向 fork 本模板后的部署和生产运维。示例命令默认从仓库根目录执行，并使用 `docker/docker-compose.yml` 中的 PostgreSQL 服务 `db`。

## 1. 基础部署

首次部署：

```bash
cp .env.example .env
# 编辑 .env，至少修改 POSTGRES_PASSWORD、SECRET_KEY、FIRST_SUPERUSER_PASSWORD
docker compose -f docker/docker-compose.yml up -d --build
```

后端容器启动时会先执行 Alembic 迁移：

```bash
uv run alembic -c app/alembic.ini upgrade head
```

因此常规部署只需要启动或重建容器；如果迁移失败，后端容器会启动失败，应先查看日志并修复迁移问题：

```bash
docker compose -f docker/docker-compose.yml logs backend
```

## 2. PostgreSQL 备份

推荐使用 PostgreSQL 逻辑备份，并把备份文件保存到宿主机目录。以下命令会读取 `db` 容器内的 `POSTGRES_USER` 和 `POSTGRES_DB` 环境变量，生成自定义格式备份文件。

```bash
mkdir -p backups
docker compose -f docker/docker-compose.yml exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "backups/app_$(date +%Y%m%d_%H%M%S).dump"
```

备份完成后至少做两件事：

1. 将备份文件复制到服务器以外的安全位置。
2. 定期在临时数据库或测试环境执行恢复演练，确认备份可用。

上传文件不在 PostgreSQL 中。Docker 模式下上传内容保存在 `backend-uploads` volume，数据库备份不会包含这些文件。若你的派生项目已经依赖上传文件，需要单独备份该 volume。

## 3. PostgreSQL 恢复

恢复会覆盖目标数据库。生产恢复前请先停止后端，避免恢复过程中仍有写入请求。

```bash
BACKUP=backups/app_20260512_120000.dump

docker compose -f docker/docker-compose.yml stop backend
docker compose -f docker/docker-compose.yml exec -T db sh -c 'dropdb -U "$POSTGRES_USER" --if-exists "$POSTGRES_DB" && createdb -U "$POSTGRES_USER" "$POSTGRES_DB"'
docker compose -f docker/docker-compose.yml exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists' < "$BACKUP"
docker compose -f docker/docker-compose.yml run --rm backend uv run alembic -c app/alembic.ini upgrade head
docker compose -f docker/docker-compose.yml up -d backend frontend
```

恢复后检查服务状态和后端日志：

```bash
docker compose -f docker/docker-compose.yml ps
docker compose -f docker/docker-compose.yml logs backend
```

如果恢复到的是旧版本备份，必须在恢复后运行 `upgrade head`，让数据库结构升级到当前代码版本。

## 4. 迁移升级流程

生产升级建议按以下顺序执行：

1. 确认当前版本运行正常，并记录当前镜像、Git commit 或发布包版本。
2. 执行一次 PostgreSQL 逻辑备份，并确认备份文件已经离开服务器或进入可靠的备份系统。
3. 在测试环境用同一份备份恢复，再执行迁移，确认迁移能成功完成。
4. 在生产环境拉取新代码或新镜像。
5. 重建并启动服务：

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

6. 查看后端日志，确认 Alembic 迁移执行成功：

```bash
docker compose -f docker/docker-compose.yml logs backend
```

7. 登录管理后台，检查用户、角色、权限、审计日志、系统设置和上传资源是否正常。

如果需要先手动执行迁移而不是随后端启动执行，可以运行：

```bash
docker compose -f docker/docker-compose.yml run --rm backend uv run alembic -c app/alembic.ini upgrade head
```

## 5. 回滚原则

数据库迁移一旦在生产环境执行，不要只回退代码而不处理数据库。推荐回滚方式是：

1. 停止后端服务。
2. 部署上一个稳定版本的代码或镜像。
3. 使用升级前的备份恢复数据库。
4. 启动服务并检查日志。

除非迁移脚本已经明确验证过可逆，不建议在生产环境依赖 `alembic downgrade` 作为唯一回滚手段。
