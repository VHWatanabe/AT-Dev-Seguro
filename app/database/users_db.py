from app.models.user import User, Role
from app.auth.security import hash_password

users_db: dict[str, User] = {
    "ana.recepcao": User(
        id=1, username="ana.recepcao",
        hashed_password=hash_password("senha123"),
        role=Role.recepcionista,
    ),
    "dr.carlos": User(
        id=2, username="dr.carlos",
        hashed_password=hash_password("senha123"),
        role=Role.profissional_saude,
    ),
    "dra.beatriz": User(
        id=4, username="dra.beatriz",
        hashed_password=hash_password("senha123"),
        role=Role.profissional_saude,
    ),
    "admin": User(
        id=3, username="admin",
        hashed_password=hash_password("senha123"),
        role=Role.administrador,
    ),
}