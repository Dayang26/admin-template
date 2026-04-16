import uuid

from fastapi import APIRouter, Query
from fastapi.params import Depends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import col, select

from app.deps import SessionDep
from app.deps.auth import get_current_active_superuser
from app.models.db import Class
from app.schemas import Response
from app.schemas.user_class import ClassCreateReq, ClassPublicResp, ClassUpdateReq
from app.services import class_service

router = APIRouter(prefix="/admin/classes", tags=["admin/classes"])


@router.get("/", dependencies=[Depends(get_current_active_superuser)], response_model=Response[Page[ClassPublicResp]])
def get_classes(
    session: SessionDep,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    name: str | None = Query(None, description="Search by class name (fuzzy match)"),
) -> Response[Page[ClassPublicResp]]:
    """Retrieve classes with pagination and optional fuzzy search by name."""
    statement = select(Class)
    if name:
        statement = statement.where(col(Class.name).ilike(f"%{name}%"))
    statement = statement.order_by(col(Class.created_at).desc())

    page_data = paginate(
        session,
        statement,
        params=Params(page=page, size=size),
        transformer=lambda classes: [ClassPublicResp.model_validate(c) for c in classes],
    )
    return Response.ok(data=page_data)


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=Response[ClassPublicResp], status_code=201)
def create_class(*, session: SessionDep, class_in: ClassCreateReq) -> Response[ClassPublicResp]:
    """Create a new class. Only accessible by superusers."""
    db_class = class_service.create_class(session=session, class_create=class_in)
    return Response.ok(data=ClassPublicResp.model_validate(db_class), code=201)


@router.get("/{class_id}", dependencies=[Depends(get_current_active_superuser)], response_model=Response[ClassPublicResp])
def get_class(*, session: SessionDep, class_id: uuid.UUID) -> Response[ClassPublicResp]:
    """Get a specific class by ID. Only accessible by superusers."""
    db_class = class_service.get_class(session=session, class_id=class_id)
    return Response.ok(data=ClassPublicResp.model_validate(db_class))


@router.patch("/{class_id}", dependencies=[Depends(get_current_active_superuser)], response_model=Response[ClassPublicResp])
def update_class(*, session: SessionDep, class_id: uuid.UUID, class_in: ClassUpdateReq) -> Response[ClassPublicResp]:
    """Update a class by ID. Only accessible by superusers."""
    db_class = class_service.update_class(session=session, class_id=class_id, class_update=class_in)
    return Response.ok(data=ClassPublicResp.model_validate(db_class))


@router.delete("/{class_id}", dependencies=[Depends(get_current_active_superuser)], response_model=Response[None])
def delete_class(*, session: SessionDep, class_id: uuid.UUID) -> Response[None]:
    """Delete a class by ID. Only accessible by superusers."""
    class_service.delete_class(session=session, class_id=class_id)
    return Response.ok(data=None)
