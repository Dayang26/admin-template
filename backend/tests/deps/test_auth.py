import uuid

import jwt
import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.deps.auth import get_current_user
from app.models.Token import TokenPayload


def test_get_current_user_invalid_token(session: Session) -> None:
    """Test get_current_user with an invalid token."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(session=session, token="invalid-token-string")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


def test_get_current_user_missing_sub(session: Session) -> None:
    """Test get_current_user with a valid token but missing 'sub' (validation error)."""
    # Create a token without 'sub'
    payload = {"exp": 1234567890}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=security.ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(session=session, token=token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


def test_get_current_user_not_found(session: Session) -> None:
    """Test get_current_user with a token for a non-existent user."""
    fake_id = str(uuid.uuid4())
    token_data = TokenPayload(sub=fake_id)
    token = security.create_access_token(token_data.sub)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(session=session, token=token)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
