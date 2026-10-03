from fastapi.testclient import TestClient
from app.main import app
from tests.test_auth import obter_token

client = TestClient(app)


def obter_token_cliente(client_id: str, client_secret: str) -> str:
    response = client.post(
        "/auth/token/client",
        data={"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret},
    )
    return response.json()["access_token"]


def test_laboratorio_acessa_horarios_com_escopo_correto():
    token = obter_token_cliente("laboratorio-parceiro", "segredo-lab-123")
    response = client.get(
        "/laboratorio/horarios-ocupados",
        params={"profissional_id": 2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_token_de_profissional_nao_acessa_rota_do_laboratorio():
    token = obter_token("dr.carlos", "senha123")
    response = client.get(
        "/laboratorio/horarios-ocupados",
        params={"profissional_id": 2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401