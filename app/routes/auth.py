from fastapi import APIRouter, HTTPException, Depends, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.database.users_db import users_db
from app.database.clients_db import clients_db
from app.auth.security import (
    verify_password,
    create_temp_token,
    create_access_token,
    decode_token,
    create_client_token,
)
from app.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["auth"])

MFA_CODE_SIMULADO = "123456"


class MFARequest(BaseModel):
    temp_token: str
    codigo: str


@router.post("/token")
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    temp_token = create_temp_token(user.username)
    return {"temp_token": temp_token, "detail": "Credenciais válidas. Informe o código MFA."}


@router.post("/mfa/verify")
def verify_mfa(dados: MFARequest):
    payload = decode_token(dados.temp_token, expected_scope="mfa_pending")
    if dados.codigo != MFA_CODE_SIMULADO:
        raise HTTPException(status_code=401, detail="Código MFA inválido")
    user = users_db.get(payload["sub"])
    access_token = create_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token/client")
def login_client(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
):
    if grant_type != "client_credentials":
        raise HTTPException(status_code=400, detail="grant_type deve ser client_credentials")
    client = clients_db.get(client_id)
    if not client or not verify_password(client_secret, client.client_secret_hash):
        raise HTTPException(status_code=401, detail="Credenciais de cliente inválidas")
    token = create_client_token(client.client_id, client.scopes)
    return {"access_token": token, "token_type": "bearer"}