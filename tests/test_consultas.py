from fastapi.testclient import TestClient
from app.main import app
from tests.test_auth import obter_token

client = TestClient(app)


def test_criar_consulta_sucesso():
    token = obter_token("dr.carlos", "senha123")
    payload = {
        "paciente_id": 1,
        "profissional_id": 2,
        "data_hora": "2026-10-01T14:30:00",
        "status": "agendada",
    }
    response = client.post("/consultas/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["paciente_id"] == 1
    assert "id" in data


def test_observacoes_internas_nao_vaza():
    token = obter_token("dr.carlos", "senha123")
    payload = {
        "paciente_id": 5,
        "profissional_id": 2,
        "data_hora": "2026-11-01T09:00:00",
        "status": "agendada",
    }
    response = client.post("/consultas/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert "observacoes_internas" not in response.json()


def test_bola_leitura_bloqueada_para_profissional_sem_ownership():
    token_dr_carlos = obter_token("dr.carlos", "senha123")
    payload = {
        "paciente_id": 9,
        "profissional_id": 2,
        "data_hora": "2026-12-01T10:00:00",
        "status": "agendada",
    }
    criada = client.post("/consultas/", json=payload, headers={"Authorization": f"Bearer {token_dr_carlos}"})
    consulta_id = criada.json()["id"]

    token_admin = obter_token("admin", "senha123")
    response_admin = client.get(f"/consultas/{consulta_id}", headers={"Authorization": f"Bearer {token_admin}"})
    assert response_admin.status_code == 200


def test_campo_extra_rejeitado_mass_assignment():
    token = obter_token("dr.carlos", "senha123")
    payload = {
        "paciente_id": 1,
        "profissional_id": 2,
        "data_hora": "2026-10-01T14:30:00",
        "status": "agendada",
        "campo_nao_declarado": "tentativa de mass assignment",
    }
    response = client.post("/consultas/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


def test_status_invalido_rejeitado_pela_whitelist():
    token = obter_token("dr.carlos", "senha123")
    payload = {
        "paciente_id": 1,
        "profissional_id": 2,
        "data_hora": "2026-10-01T14:30:00",
        "status": "<script>alert(1)</script>",
    }
    response = client.post("/consultas/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422