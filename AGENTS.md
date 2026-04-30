# AGENTS.md

This repository is a reusable admin boilerplate, not a business application.
All agents working in this repo must keep the template small, generic, and easy to fork.

## Product Boundary

- Treat this project as a generic RBAC admin template.
- Do not add domain-specific concepts such as classes, courses, orders, products, tenants, carriers, teachers, students, workflows, or billing unless the user explicitly asks for that business module.
- Keep built-in features limited to common admin infrastructure:
  - authentication and current-user profile
  - user management
  - role and permission management
  - audit logs
  - dashboard overview
  - image upload for public branding assets
  - system branding settings
- System settings are only for branding and public display data:
  - system name
  - tagline
  - copyright
  - page title template
  - light/dark logo
  - favicon
  - login background image
- Do not put frontend runtime behavior into system settings. Layout mode, default home path, request timeout, mock switches, keep-alive, route cache, animations, token expiry, SSO, captcha, and password policy belong in source code, environment variables, or future explicit feature work.

## Avoid Overengineering

- Prefer simple static configuration over dynamic database-driven configuration unless there is a concrete user request.
- Do not implement a full dictionary management system for this template by default.
- For labels and small option lists, use local frontend mapping files near the relevant feature.
- Only consider a database-backed dictionary system inside a real business project that needs non-developer operators to edit enum values at runtime.
- Do not add Redis, queues, background workers, SSO, email, SMS, webhooks, feature flags, or cloud storage providers as placeholders. Add them only when the feature is fully implemented and tested.

## Backend Rules

- Framework: FastAPI + SQLModel + PostgreSQL + Alembic.
- Use explicit response models and `Response.ok(...)`; do not reintroduce automatic response-wrapping middleware unless the whole router layer is intentionally refactored.
- Protect admin routes with `require_permission(resource, action)`.
- Keep `superuser` as the only built-in role unless the user explicitly asks for more built-in roles.
- New permissions must be seeded in `backend/app/core/db.py` and included in tests.
- New database models must be imported from `backend/app/models/db/__init__.py` so Alembic can detect them.
- Every model change must include an Alembic migration.
- Admin create/update/delete operations should write audit logs.
- Uploads must remain conservative:
  - local storage is the default
  - public uploads are directly served
  - private uploads require future explicit authenticated download work
  - validate extension, MIME type, file signature, file size, and field lengths
  - clean up saved files if DB persistence fails
- Do not store cloud provider secrets in database-backed admin settings unless a secure secret-management design is explicitly requested.

## Frontend Rules

- Framework: React + Vite + TypeScript + Tailwind CSS + shadcn-style components.
- Keep route guards permission-based. Sidebar visibility and route access must use the same permission model.
- Do not add role-only admin guards when a permission guard is available.
- Keep admin layout fixed as the template layout. Do not add dynamic layout configuration without explicit user request.
- Theme selection is a local frontend preference, not a backend system setting.
- System branding can be read from public system settings and used for title, logo, favicon, login background, and display text.
- Prefer small, feature-local utilities over global abstractions.
- Do not add a generic DataTable, dictionary framework, or form framework unless at least two real screens need it.
- Do not keep unused default Vite assets, unused dependencies, or demo code.

## Documentation Rules

- Documentation must describe the current implementation, not aspirational features.
- If a capability is not implemented, put it under a clear "future work" or "optional extension" section.
- Keep README, template guide, architecture docs, Docker docs, and Makefile commands consistent.
- When adding or removing a command, update the docs in the same change.
- RBAC extension examples must match current backend style:
  - `response_model=Response[...]`
  - `Response.ok(...)`
  - `SessionDep`
  - `AuditInfo`
  - `log_audit(session, ...)`
- Do not document frontend tests, E2E, Redis, email, SSO, or dynamic dictionaries as existing capabilities unless they are actually implemented.

## Testing And Verification

Run targeted checks for the area you touched.

Backend:

```bash
cd backend && uv run ruff check app tests
cd backend && uv run pytest tests/
```

Frontend:

```bash
cd frontend && pnpm lint
cd frontend && pnpm build
```

General:

```bash
git diff --check
```

If a command is documented in README or Makefile, it must work in a fresh checkout after dependencies are installed.

## Git Hygiene

- Do not commit `.env`, local database files, generated coverage reports, build output, dependency folders, or IDE-private files.
- `.idea/`, `frontend/dist/`, `frontend/node_modules/`, backend caches, and upload storage should stay ignored.
- Do not remove or overwrite user changes unless explicitly asked.
- Keep changes scoped to the requested task.
