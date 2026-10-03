from app.models.client import Client
from app.auth.security import hash_password

clients_db: dict[str, Client] = {
    "laboratorio-parceiro": Client(
        client_id="laboratorio-parceiro",
        client_secret_hash=hash_password("segredo-lab-123"),
        scopes=["laboratorio:horarios:leitura"],
    ),
}