from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from sqlmodel import Session
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.db import engine, init_db


def custom_generate_unique_id(route: APIRoute) -> str:
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


# SENTRY_DSN
@asynccontextmanager
async def lifespan(_: FastAPI):
    with Session(engine) as session:
        init_db(session)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

# ── 中间件注册（顺序重要：后注册先执行，CORS 在最外层）──


if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ── 异常处理器 ──────────────────────────────────────────────


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    """覆盖 FastAPI 默认的 HTTPException 处理器，统一包装错误响应。"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, _exc: RequestValidationError) -> JSONResponse:
    """覆盖 422 校验错误处理器。message 固定为 'Validation Error'，不暴露内部字段细节。"""
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "Validation Error",
            "data": None,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    """兜底处理器，捕获所有未处理异常，返回 500。"""
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "Internal Server Error",
            "data": None,
        },
    )


app.include_router(api_router, prefix=settings.API_V1_STR)
add_pagination(app)


def mount_public_uploads(fastapi_app: FastAPI) -> None:
    public_dir = Path(settings.UPLOAD_PUBLIC_DIR).resolve()
    private_dir = Path(settings.UPLOAD_PRIVATE_DIR).resolve()
    public_dir.mkdir(parents=True, exist_ok=True)
    private_dir.mkdir(parents=True, exist_ok=True)

    fastapi_app.mount(
        settings.UPLOAD_PUBLIC_URL_PREFIX,
        StaticFiles(directory=public_dir),
        name="uploads_public",
    )


mount_public_uploads(app)


@app.get("/")
async def root():
    return {"message": "Health Check ok"}
