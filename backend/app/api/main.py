from fastapi import APIRouter

from app.api.routers.admin.users import router as admin_users_router
from app.api.routers.login import router as login_router
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login_router)
api_router.include_router(admin_users_router)


# todo :: add more endpoints

if settings.ENVIRONMENT == "local":
    # todo set private router
    pass
