from fastapi import APIRouter

from app.api.routers.users import router as users_router
from app.api.routers.login import router as login_router
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(users_router)
api_router.include_router(login_router)


# todo :: add more endpoints

if settings.ENVIRONMENT == "local":
    # todo set private router
    pass
