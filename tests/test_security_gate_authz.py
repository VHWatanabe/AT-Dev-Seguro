from fastapi.testclient import TestClient
from app.main import app
from tests.test_auth import obter_token

client = TestClient(app)


def test_requisicao_sem_token_e_rejeitada():
    response = client.get("/consultas/")
    assert response.status_code == 401


def test_bfla_recepcionista_nao_acessa_rota_de_criacao():
    token = obter_token("ana.recepcao", "senha123")
    payload = {
        "paciente_id": 1,
        "profissional_id": 2,
        "data_hora": "2026-10-01T14:30:00",
        "status": "agendada",
    }
    response = client.post("/consultas/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_bola_profissional_nao_edita_consulta_de_outro():
    token_dr_carlos = obter_token("dr.carlos", "senha123")
    payload = {
        "paciente_id": 1,
        "profissional_id": 2,
        "data_hora": "2026-10-01T14:30:00",
        "status": "agendada",
    }
    criada = client.post("/consultas/", json=payload, headers={"Authorization": f"Bearer {token_dr_carlos}"})
    consulta_id = criada.json()["id"]

    token_dra_beatriz = obter_token("dra.beatriz", "senha123")
    atualizacao = {
        "paciente_id": 1,
        "profissional_id": 2,
        "data_hora": "2026-10-01T15:00:00",
        "status": "confirmada",
    }
    response = client.put(
        f"/consultas/{consulta_id}", json=atualizacao, headers={"Authorization": f"Bearer {token_dra_beatriz}"}
    )
    assert response.status_code == 403


def test_bola_profissional_nao_deleta_consulta_de_outro():
    token_dr_carlos = obter_token("dr.carlos", "senha123")
    payload = {
        "paciente_id": 1,
        "profissional_id": 2,
        "data_hora": "2026-10-01T14:30:00",
        "status": "agendada",
    }
    criada = client.post("/consultas/", json=payload, headers={"Authorization": f"Bearer {token_dr_carlos}"})
    consulta_id = criada.json()["id"]

    token_dra_beatriz = obter_token("dra.beatriz", "senha123")
    response = client.delete(
        f"/consultas/{consulta_id}", headers={"Authorization": f"Bearer {token_dra_beatriz}"}
    )
    assert response.status_code == 403