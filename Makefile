.PHONY: dev dev-backend dev-frontend test test-backend lint lint-backend lint-frontend build-frontend check db-upgrade db-revision

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && pnpm dev

# 使用 make -j2 并发运行前后端
dev:
	@echo "Starting backend and frontend concurrently..."
	$(MAKE) -j2 dev-backend dev-frontend

test-backend:
	cd backend && uv run pytest tests/

test: test-backend

lint-backend:
	cd backend && uv run ruff check .

lint-frontend:
	cd frontend && pnpm lint

lint: lint-backend lint-frontend

build-frontend:
	cd frontend && pnpm build

check: lint test build-frontend

db-upgrade:
	cd backend && uv run alembic -c app/alembic.ini upgrade head

db-revision:
	cd backend && uv run alembic -c app/alembic.ini revision --autogenerate -m "auto"
