from fastapi.testclient import TestClient

from allmaths_engine.main import app

client = TestClient(app)
H = {"X-Engine-Token": "test-token-123456"}


def test_health_is_open():
    assert client.get("/health").json() == {"status": "ok"}


def test_check_requires_token():
    body = {"answer_type": "number", "student": "2", "correct": "2"}
    assert client.post("/v1/check", json=body).status_code == 401
    assert client.post("/v1/check", json=body, headers={"X-Engine-Token": "wrong-token-xx"}).status_code == 401


def test_check_ok():
    body = {"answer_type": "number", "student": "2/sqrt(2)", "correct": "sqrt(2)"}
    r = client.post("/v1/check", json=body, headers=H)
    assert r.status_code == 200 and r.json()["status"] == "correct"


def test_check_decimal_message():
    body = {"answer_type": "number", "student": "0.5", "correct": "1/2"}
    j = client.post("/v1/check", json=body, headers=H).json()
    assert j["status"] == "invalid" and j["code"] == "decimal_not_allowed"


def test_check_validates_input():
    r = client.post("/v1/check", json={"answer_type": "bogus", "student": "1", "correct": "1"}, headers=H)
    assert r.status_code == 422
    r = client.post("/v1/check", json={"answer_type": "number", "student": "1" * 600, "correct": "1"}, headers=H)
    assert r.status_code == 422


def test_compute_and_verify():
    j = client.post("/v1/compute", json={"expression": "cross((2,-1,3),(1,4,-2))"}, headers=H).json()
    assert j["ok"] and j["text"] == "(-10, 7, 9)"
    j = client.post("/v1/verify", json={"a": "dot((2,-1,3),(1,4,-2))", "b": "-8"}, headers=H).json()
    assert j["equal"] is True
    j = client.post("/v1/verify", json={"a": "1/2", "b": "0.5"}, headers=H).json()
    assert j["equal"] is False and j["code"] == "decimal_in_content"


def test_no_openapi_docs_exposed():
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404
