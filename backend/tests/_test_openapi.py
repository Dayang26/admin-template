from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
resp = client.get("/api/v1/openapi.json")
import json

print(json.dumps(resp.json()["paths"]["/api/v1/admin/users/"]["get"], indent=2))
