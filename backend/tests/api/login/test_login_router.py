from types import SimpleNamespace

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

import app.deps as deps
from app.api.routers import login as login_router


class DummySession:
    pass


def _build_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(login_router.router, prefix="/api/v1")

    @test_app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "message": exc.detail, "data": None},
        )

    @test_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"code": 422, "message": "Validation Error", "data": None},
        )

    def override_get_db():
        yield DummySession()

    test_app.dependency_overrides[deps.get_db] = override_get_db
    return test_app


def test_login_access_token_success(monkeypatch):
    app = _build_app()
    client = TestClient(app)

    fake_user = SimpleNamespace(id="user-123", is_active=True)
    called = {}

    def fake_authenticate(*, session, email, password):
        called["email"] = email
        called["password"] = password
        called["session_type"] = type(session).__name__
        return fake_user

    def fake_create_access_token(subject, expires_delta=None):
        called["subject"] = subject
        called["expires_delta"] = expires_delta
        return "mocked.jwt.token"

    monkeypatch.setattr(login_router.login_service, "authenticate", fake_authenticate)
    monkeypatch.setattr(login_router.security, "create_access_token", fake_create_access_token)

    resp = client.post(
        "/api/v1/login/access-token",
        data={"username": "admin@example.com", "password": "secret123"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"] == "mocked.jwt.token"
    assert body["token_type"] == "bearer"
    assert called["email"] == "admin@example.com"
    assert called["password"] == "secret123"
    assert called["session_type"] == "DummySession"
    assert called["subject"] == "user-123"
    assert called["expires_delta"] is not None


def test_login_access_token_wrong_credentials(monkeypatch):
    app = _build_app()
    client = TestClient(app)

    monkeypatch.setattr(login_router.login_service, "authenticate", lambda **_: None)

    resp = client.post(
        "/api/v1/login/access-token",
        data={"username": "admin@example.com", "password": "bad-pass"},
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["code"] == 400
    assert body["message"] == "Incorrect email or password"
    assert body["data"] is None


def test_login_access_token_inactive_user(monkeypatch):
    app = _build_app()
    client = TestClient(app)

    fake_user = SimpleNamespace(id="user-123", is_active=False)
    monkeypatch.setattr(login_router.login_service, "authenticate", lambda **_: fake_user)

    resp = client.post(
        "/api/v1/login/access-token",
        data={"username": "admin@example.com", "password": "secret123"},
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["code"] == 400
    assert body["message"] == "Inactive user"
    assert body["data"] is None


def test_login_access_token_validation_error_when_form_missing():
    app = _build_app()
    client = TestClient(app)

    resp = client.post("/api/v1/login/access-token", data={"username": "admin@example.com"})

    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == 422
    assert body["message"] == "Validation Error"
    assert body["data"] is None
