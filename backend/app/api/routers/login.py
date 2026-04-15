from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core import security
from app.core.config import settings
from app.deps import SessionDep
from app.schemas.token import TokenResp
from app.services import login_service

router = APIRouter(tags=["login"])


@router.post("/login/access-token", response_model=TokenResp)
def login_access_token(session: SessionDep, from_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenResp:
    user = login_service.authenticate(session=session, email=from_data.username, password=from_data.password)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = TokenResp(
        access_token=security.create_access_token(user.id, expires_delta=access_token_expires),
    )
    return token
