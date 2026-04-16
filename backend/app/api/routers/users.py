from fastapi import APIRouter
from app.deps import SessionDep
from app.deps.auth import CurrentUser
from app.schemas import Response, UserPublicResp, UserUpdateMeReq
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me", response_model=Response[UserPublicResp])
def update_user_me(
    *,
    session: SessionDep,
    user_in: UserUpdateMeReq,
    current_user: CurrentUser,
) -> Response[UserPublicResp]:
    """
    Update own user profile information.
    Currently only allows updating:
    - **full_name**
    """
    user = user_service.update_user_me(session=session, user_update=user_in, current_user=current_user)
    return Response.ok(data=UserPublicResp.model_validate(user))
