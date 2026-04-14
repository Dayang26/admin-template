from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import deps
from app.api.routers import login as login_router


class DummySession:
    pass


def _build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(login_router.router, prefix="/api/v1")

    def override_get_db():
        yield DummySession()

    app.dependency_overrides[deps.get_db] = override_get_db
    return app


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
    assert resp.json() == {"access_token": "mocked.jwt.token", "token_type": "bearer"}
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
    assert resp.json() == {"detail": "Incorrect email or password"}


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
    assert resp.json() == {"detail": "Inactive user"}


def test_login_access_token_validation_error_when_form_missing():
    app = _build_app()
    client = TestClient(app)

    resp = client.post("/api/v1/login/access-token", data={"username": "admin@example.com"})

    assert resp.status_code == 422
