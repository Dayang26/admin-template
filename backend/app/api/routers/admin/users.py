from app.deps import SessionDep
from app.deps.auth import get_current_active_superuser
from app.models.db import User
from app.schemas import UserPublic
from fastapi import APIRouter
from fastapi.params import Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import col, select

router = APIRouter(prefix="/admin/users", tags=["admin"])


@router.get("/", dependencies=[Depends(get_current_active_superuser)], response_model=Page[UserPublic])
def get_users(session: SessionDep) -> Page[UserPublic]:
    """Retrieve users with pagination."""
    statement = select(User).order_by(col(User.created_at).desc())
    return paginate(
        session,
        statement,
        transformer=lambda users: [UserPublic.model_validate(user) for user in users],
    )
