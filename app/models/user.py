from enum import Enum
from pydantic import BaseModel


class Role(str, Enum):
    recepcionista = "recepcionista"
    profissional_saude = "profissional_saude"
    administrador = "administrador"


class User(BaseModel):
    id: int
    username: str
    hashed_password: str
    role: Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    id: int
    username: str
    role: Role