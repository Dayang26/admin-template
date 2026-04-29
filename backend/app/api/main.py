from fastapi import APIRouter

from app.api.routers import login, uploads, users
from app.api.routers.admin.audit_logs import router as admin_audit_logs_router
from app.api.routers.admin.dashboard import router as admin_dashboard_router
from app.api.routers.admin.roles import router as admin_roles_router
from app.api.routers.admin.system_settings import router as admin_system_settings_router
from app.api.routers.admin.users import router as admin_users_router
from app.api.routers.system_settings import router as system_settings_router
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(admin_users_router)
api_router.include_router(admin_dashboard_router)
api_router.include_router(admin_roles_router)
api_router.include_router(admin_audit_logs_router)
api_router.include_router(uploads.router)
api_router.include_router(system_settings_router)
api_router.include_router(admin_system_settings_router)


# todo :: add more endpoints

if settings.ENVIRONMENT == "local":
    # todo set private router
    pass
