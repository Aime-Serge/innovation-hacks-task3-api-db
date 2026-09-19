from contextlib import contextmanager


def test_health_reports_database_connected(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["database"] == "ok" and r.json()["status"] == "ok"


def test_health_returns_503_when_the_database_is_unreachable(client, monkeypatch):
    @contextmanager
    def broken():
        raise RuntimeError("connection refused")
        yield

    monkeypatch.setattr("app.main.session_scope", broken)
    r = client.get("/health")
    assert r.status_code == 503
    assert r.json()["status"] == "degraded" and r.json()["database"] == "unavailable"
    assert "connection refused" not in r.text
