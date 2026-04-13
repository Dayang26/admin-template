from fastapi import APIRouter

from app.core.config import settings

api_router = APIRouter()


# todo :: add more endpoints

if settings.ENVIRONMENT == "local":
    # todo set private router
    pass
