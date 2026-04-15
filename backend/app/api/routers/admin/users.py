import uuid

from app.deps import SessionDep
from app.deps.auth import CurrentUser, get_current_active_superuser
from app.models.db import User
from app.schemas import UserCreateByAdmin, UserPublic, UserUpdateReq
from app.services import user_service
from fastapi import APIRouter, HTTPException
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


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic, status_code=201)
def create_user_by_admin(*, session: SessionDep, user_in: UserCreateByAdmin) -> UserPublic:
    """Create a new user with role assignment. Only accessible by superusers."""
    user = user_service.create_user_with_roles(session=session, user_create=user_in)
    return UserPublic.model_validate(user)


@router.patch("/{user_id}", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
def update_user_by_admin(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdateReq,
    current_user: CurrentUser,
) -> UserPublic:
    """Update a user's information by admin (superuser).

    - **full_name**: Update the user's full name
    - **password**: Update the user's password
    - **is_active**: Activate or deactivate the user account
    - **roles**: Replace the user's roles (clear old roles and bind new ones)

    Special restriction: Cannot modify other superusers' information.
    """
    user = user_service.update_user_by_admin(
        session=session,
        user_update=user_in,
        target_user_id=user_id,
        current_user_id=current_user.id,
    )
    return UserPublic.model_validate(user)