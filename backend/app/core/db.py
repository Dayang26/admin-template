from sqlalchemy import create_engine
from sqlmodel import Session, select

from app.core.config import settings
from app.models.UserModels import User, UserCreateReq
from app.services import UserServices

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    user = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER).first())

    if not user:
        user_int = UserCreateReq(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            is_active=True,
        )
        user = UserServices.create_user(session=session, user_create=user_int)
