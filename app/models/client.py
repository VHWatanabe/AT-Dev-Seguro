from pydantic import BaseModel


class Client(BaseModel):
    client_id: str
    client_secret_hash: str
    scopes: list[str]


class ClientTokenData(BaseModel):
    client_id: str
    scopes: list[str]