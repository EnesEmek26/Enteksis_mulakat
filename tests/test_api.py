import os
from datetime import datetime, timezone

# main.py içe aktarılmadan önce ayarlanmalı. Gerçek veritabanı kullanılmaz.
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
os.environ["ADMIN_TOKEN"] = "test-token"

import psycopg
import pytest
from fastapi.testclient import TestClient

from app import main

VALID = {
    "name": "Test Kullanici",
    "email": "test@example.com",
    "service": "gorev-toplama",
    "message": "Bu bir test mesajidir.",
}


class FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    def fetchone(self):
        return self._rows[0]

    def fetchall(self):
        return self._rows


class FakeConn:
    def __init__(self, state):
        self.state = state

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        if self.state["fail"]:
            raise psycopg.OperationalError("db down")
        if sql.lstrip().upper().startswith("INSERT"):
            new_id = len(self.state["rows"]) + 1
            name, email, service, message = params
            self.state["rows"].append(
                (new_id, name, email, service, message, datetime.now(timezone.utc))
            )
            return FakeCursor([(new_id,)])
        if sql.lstrip().upper().startswith("SELECT COUNT"):
            return FakeCursor([(len(self.state["rows"]),)])
        return FakeCursor(list(reversed(self.state["rows"])))


@pytest.fixture
def db(monkeypatch):
    state = {"rows": [], "fail": False}
    monkeypatch.setattr(main.psycopg, "connect", lambda *a, **k: FakeConn(state))
    return state


@pytest.fixture
def client(db):
    # "with" kullanılmadığı için startup (init_db) çalışmaz.
    return TestClient(main.app)


def test_valid_request_is_saved(client, db):
    res = client.post("/api/requests", json=VALID)
    assert res.status_code == 201
    assert res.json()["id"] == 1
    assert len(db["rows"]) == 1


def test_input_is_trimmed(client, db):
    res = client.post("/api/requests", json={**VALID, "name": "  Test Kullanici  "})
    assert res.status_code == 201
    assert db["rows"][0][1] == "Test Kullanici"


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", ""),
        ("name", "A"),
        ("email", "gecersiz"),
        ("service", "yok"),
        ("message", "kisa"),
        ("message", "x" * 1001),
    ],
)
def test_invalid_field_is_rejected_and_not_saved(client, db, field, value):
    res = client.post("/api/requests", json={**VALID, field: value})
    assert res.status_code == 422
    assert field in res.json()["errors"]
    assert db["rows"] == []


def test_missing_field_is_rejected(client, db):
    body = {k: v for k, v in VALID.items() if k != "email"}
    res = client.post("/api/requests", json=body)
    assert res.status_code == 422
    assert "email" in res.json()["errors"]
    assert db["rows"] == []


def test_honeypot_is_rejected(client, db):
    res = client.post("/api/requests", json={**VALID, "website": "http://spam.example"})
    assert res.status_code == 400
    assert db["rows"] == []


def test_db_failure_returns_500_without_id(client, db):
    db["fail"] = True
    res = client.post("/api/requests", json=VALID)
    assert res.status_code == 500
    assert "id" not in res.json()
    assert "db down" not in res.text  # iç hata detayı sızmamalı


def test_admin_list_requires_token(client):
    assert client.get("/api/requests").status_code == 401
    assert client.get("/api/requests", headers={"X-Admin-Token": "yanlis"}).status_code == 401


def test_admin_list_with_token(client, db):
    client.post("/api/requests", json=VALID)
    res = client.get("/api/requests", headers={"X-Admin-Token": "test-token"})
    assert res.status_code == 200
    assert res.json()[0]["email"] == "test@example.com"


def test_health_reports_count(client, db):
    client.post("/api/requests", json=VALID)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["kayit_sayisi"] == 1