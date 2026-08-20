import os
from pathlib import Path

TEST_DB = Path("/tmp/deadinternet_test.db")
os.environ["DEADINTERNET_DB_PATH"] = str(TEST_DB)

from fastapi.testclient import TestClient
from app.main import app


def setup_function():
    TEST_DB.unlink(missing_ok=True)


def test_crud_and_duplicate_url():
    with TestClient(app) as client:
        payload = {"platform":"instagram","url":"https://example.com/reel/1","title":"Teste","views":1000,"likes":100,"comments":10,"hook_strength":8,"recreation_ease":7,"monetization_potential":6}
        created = client.post("/api/references", json=payload)
        assert created.status_code == 201
        reference_id = created.json()["id"]
        assert created.json()["score"] > 0
        assert client.post("/api/references", json=payload).status_code == 409
        assert client.patch(f"/api/references/{reference_id}", json={"status":"selected"}).json()["status"] == "selected"
        assert client.delete(f"/api/references/{reference_id}").status_code == 204
        assert client.get(f"/api/references/{reference_id}").status_code == 404
