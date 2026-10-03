from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.auth.security import get_current_user
from app.models.user import TokenData, Role

client = TestClient(app)


def test_entrada_com_tipo_invalido_rejeitada_por_validacao():
    app.dependency_overrides[get_current_user] = lambda: TokenData(
        id=2, username="dr.carlos", role=Role.profissional_saude
    )
    payload = {
        "paciente_id": "nao-e-um-numero",
        "profissional_id": 2,
        "data_hora": "2026-10-01T14:30:00",
        "status": "agendada",
    }
    response = client.post("/consultas/", json=payload)
    assert response.status_code == 422
    app.dependency_overrides.clear()


def test_autorizacao_com_usuario_mockado_sem_papel_adequado():
    usuario_mockado = MagicMock(spec=TokenData)
    usuario_mockado.role = Role.recepcionista
    usuario_mockado.id = 1
    usuario_mockado.username = "ana.recepcao"

    app.dependency_overrides[get_current_user] = lambda: usuario_mockado
    payload = {
        "paciente_id": 1,
        "profissional_id": 2,
        "data_hora": "2026-10-01T14:30:00",
        "status": "agendada",
    }
    response = client.post("/consultas/", json=payload)
    assert response.status_code == 403
    app.dependency_overrides.clear()


def test_autorizacao_com_usuario_mockado_papel_adequado():
    usuario_mockado = MagicMock(spec=TokenData)
    usuario_mockado.role = Role.administrador
    usuario_mockado.id = 3
    usuario_mockado.username = "admin"

    app.dependency_overrides[get_current_user] = lambda: usuario_mockado
    payload = {
        "paciente_id": 1,
        "profissional_id": 2,
        "data_hora": "2026-10-01T14:30:00",
        "status": "agendada",
    }
    response = client.post("/consultas/", json=payload)
    assert response.status_code == 201
    app.dependency_overrides.clear()