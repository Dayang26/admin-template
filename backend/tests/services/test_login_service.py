from types import SimpleNamespace

from app.services import login_service


class FakeSession:
    def __init__(self):
        self.add_called = 0
        self.commit_called = 0
        self.refresh_called = 0

    def add(self, _obj):
        self.add_called += 1

    def commit(self):
        self.commit_called += 1

    def refresh(self, _obj):
        self.refresh_called += 1


def test_authenticate_returns_none_when_user_not_found(monkeypatch):
    session = FakeSession()
    captured = {}

    monkeypatch.setattr(login_service, "get_user_by_email", lambda **_: None)

    def fake_verify_password(plain_password, hashed_password):
        captured["plain_password"] = plain_password
        captured["hashed_password"] = hashed_password
        return False, None

    monkeypatch.setattr(login_service, "verify_password", fake_verify_password)

    user = login_service.authenticate(session=session, email="absent@example.com", password="secret123")

    assert user is None
    assert captured["plain_password"] == "secret123"
    assert captured["hashed_password"] == login_service.DUMMY_HASH
    assert session.add_called == 0
    assert session.commit_called == 0
    assert session.refresh_called == 0


def test_authenticate_returns_none_when_password_invalid(monkeypatch):
    session = FakeSession()
    db_user = SimpleNamespace(hashed_password="old-hash")

    monkeypatch.setattr(login_service, "get_user_by_email", lambda **_: db_user)
    monkeypatch.setattr(login_service, "verify_password", lambda *_: (False, None))

    user = login_service.authenticate(session=session, email="admin@example.com", password="wrong")

    assert user is None
    assert session.add_called == 0
    assert session.commit_called == 0
    assert session.refresh_called == 0


def test_authenticate_updates_hash_when_needed(monkeypatch):
    session = FakeSession()
    db_user = SimpleNamespace(hashed_password="old-hash")

    monkeypatch.setattr(login_service, "get_user_by_email", lambda **_: db_user)
    monkeypatch.setattr(login_service, "verify_password", lambda *_: (True, "new-hash"))

    user = login_service.authenticate(session=session, email="admin@example.com", password="secret123")

    assert user is db_user
    assert db_user.hashed_password == "new-hash"
    assert session.add_called == 1
    assert session.commit_called == 1
    assert session.refresh_called == 1


def test_authenticate_no_rehash_when_hash_is_current(monkeypatch):
    session = FakeSession()
    db_user = SimpleNamespace(hashed_password="current-hash")

    monkeypatch.setattr(login_service, "get_user_by_email", lambda **_: db_user)
    monkeypatch.setattr(login_service, "verify_password", lambda *_: (True, None))

    user = login_service.authenticate(session=session, email="admin@example.com", password="secret123")

    assert user is db_user
    assert db_user.hashed_password == "current-hash"
    assert session.add_called == 0
    assert session.commit_called == 0
    assert session.refresh_called == 0
