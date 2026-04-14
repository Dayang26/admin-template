from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, require_permission
from app.schemas.user import UserCreate, UserPublic
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", dependencies=[Depends(require_permission("user", "create"))], response_model=UserPublic)
def create_user(*, session: SessionDep, user_in: UserCreate) -> UserPublic:
    user = user_service.create_user(session=session, user_create=user_in)
    return user
