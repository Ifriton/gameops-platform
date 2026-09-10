from sqlalchemy.exc import OperationalError


def test_health(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness(client):
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_reports_database_failure(client, monkeypatch):
    class BrokenEngine:
        def connect(self):
            raise OperationalError("SELECT 1", {}, Exception("unavailable"))

    monkeypatch.setattr(client.app.state, "engine", BrokenEngine())
    response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
