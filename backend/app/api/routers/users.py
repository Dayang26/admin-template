from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, get_current_active_superuser
from app.schemas.user import UserCreate, UserPublic
from app.services import UserServices

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
def create_user(*, session: SessionDep, user_in: UserCreate) -> UserPublic:
    user = UserServices.create_user(session=session, user_create=user_in)
    return user
