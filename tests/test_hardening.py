from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_headers_de_seguranca_presentes():
    response = client.get("/")
    assert response.headers["strict-transport-security"] == "max-age=63072000; includeSubDomains"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_rate_limiting_bloqueia_apos_limite():
    for _ in range(5):
        client.post("/auth/token", data={"username": "dr.carlos", "password": "senha_errada"})
    response = client.post("/auth/token", data={"username": "dr.carlos", "password": "senha_errada"})
    assert response.status_code == 429