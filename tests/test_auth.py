from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
MFA_CODE = "123456"


def obter_token(username: str, password: str) -> str:
    login_response = client.post("/auth/token", data={"username": username, "password": password})
    temp_token = login_response.json()["temp_token"]
    mfa_response = client.post("/auth/mfa/verify", json={"temp_token": temp_token, "codigo": MFA_CODE})
    return mfa_response.json()["access_token"]


def test_usuario_sem_papel_admin_acesso_negado_rota_restrita():
    token = obter_token("ana.recepcao", "senha123")
    response = client.get("/admin/relatorio", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_administrador_acessa_rota_restrita():
    token = obter_token("admin", "senha123")
    response = client.get("/admin/relatorio", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200