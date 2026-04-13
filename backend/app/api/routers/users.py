from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, get_current_active_superuser
from app.models.UserModels import UserCreateReq, UserPublicResp

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublicResp)
def create_user(*, session: SessionDep, user_in: UserCreateReq) -> Any:

    return user_in
