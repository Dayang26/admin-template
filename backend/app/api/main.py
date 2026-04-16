from fastapi import APIRouter

from app.api.routers import login, users
from app.api.routers.admin.classes import router as admin_classes_router
from app.api.routers.admin.users import router as admin_users_router
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(admin_users_router)
api_router.include_router(admin_classes_router)


# todo :: add more endpoints

if settings.ENVIRONMENT == "local":
    # todo set private router
    pass
