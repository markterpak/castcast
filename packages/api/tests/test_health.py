from fastapi.testclient import TestClient

from castcast_api.main import app


def test_health_reports_ok_and_environment() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["env"] in {"local", "dev", "prod"}
    assert body["version"] == app.version
