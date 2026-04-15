import uuid

from fastapi import APIRouter, Query
from fastapi.params import Depends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import col, select

from app.deps import SessionDep
from app.deps.auth import CurrentUser, get_current_active_superuser
from app.models.db import User
from app.schemas import Response, UserCreateByAdmin, UserPublic, UserUpdateReq
from app.services import user_service

router = APIRouter(prefix="/admin/users", tags=["admin"])


@router.get("/", dependencies=[Depends(get_current_active_superuser)], response_model=Response[Page[UserPublic]])
def get_users(
    session: SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
) -> Response[Page[UserPublic]]:
    """Retrieve users with pagination."""
    statement = select(User).order_by(col(User.created_at).desc())
    page_data = paginate(
        session,
        statement,
        params=Params(page=page, size=size),
        transformer=lambda users: [UserPublic.model_validate(user) for user in users],
    )
    return Response.ok(data=page_data)


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=Response[UserPublic], status_code=201)
def create_user_by_admin(*, session: SessionDep, user_in: UserCreateByAdmin) -> Response[UserPublic]:
    """Create a new user with role assignment. Only accessible by superusers."""
    user = user_service.create_user_with_roles(session=session, user_create=user_in)
    return Response.ok(data=UserPublic.model_validate(user), code=201)


@router.patch("/{user_id}", dependencies=[Depends(get_current_active_superuser)], response_model=Response[UserPublic])
def update_user_by_admin(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdateReq,
    current_user: CurrentUser,
) -> Response[UserPublic]:
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
    return Response.ok(data=UserPublic.model_validate(user))
