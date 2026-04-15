import time
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.core.config import settings
from app.models.db import User
from app.main import app
from tests.conftest import test_engine, _get_superuser_token_headers

with test_engine.connect() as conn:
    txn = conn.begin()
    with Session(bind=conn, join_transaction_mode="create_savepoint") as session:
        from app.deps.db import get_db

        def _override():
            yield session

        app.dependency_overrides[get_db] = _override

        headers = _get_superuser_token_headers(session)
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get(f"{settings.API_V1_STR}/admin/users/", headers=headers)
        print(f"STATUS: {resp.status_code}")
        print(f"BODY: {resp.text}")
    txn.rollback()
    app.dependency_overrides.pop(get_db, None)
