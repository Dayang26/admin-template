import logging

from sqlalchemy import create_engine
from sqlmodel import Session, select

from app.core.config import settings
from app.models.db import Role, User, UserRole
from app.schemas.user import UserCreate
from app.services import user_service

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
logger = logging.getLogger(__name__)
SUPERUSER_ROLE_NAME = "superuser"


def init_db(session: Session) -> None:
    if len(settings.FIRST_SUPERUSER_PASSWORD) < 8:
        raise RuntimeError("FIRST_SUPERUSER_PASSWORD must be at least 8 characters for bootstrap user creation.")

    role = session.exec(select(Role).where(Role.name == SUPERUSER_ROLE_NAME)).first()
    if not role:
        role = Role(name=SUPERUSER_ROLE_NAME, description="Built-in unrestricted role")
        session.add(role)
        session.commit()
        session.refresh(role)
        logger.info("Created default role: %s", SUPERUSER_ROLE_NAME)

    user = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
    if not user:
        user_int = UserCreate(email=settings.FIRST_SUPERUSER, password=settings.FIRST_SUPERUSER_PASSWORD, is_active=True, full_name="superuser")
        user = user_service.create_user(session=session, user_create=user_int)
        logger.info("Created default superuser user: %s", settings.FIRST_SUPERUSER)

    user_role = session.exec(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id,
            UserRole.class_id.is_(None),
        )
    ).first()
    if not user_role:
        session.add(UserRole(user_id=user.id, role_id=role.id, class_id=None))
        session.commit()
        logger.info("Bound user %s to role %s", settings.FIRST_SUPERUSER, SUPERUSER_ROLE_NAME)
