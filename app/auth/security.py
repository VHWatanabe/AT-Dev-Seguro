from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from app.models.user import TokenData, Role, User
from app.models.client import ClientTokenData
from app.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
TEMP_TOKEN_EXPIRE_MINUTES = 5
M2M_TOKEN_EXPIRE_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user.username, "id": user.id, "role": user.role.value, "exp": expire, "scope": "access"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)


def create_temp_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=TEMP_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire, "scope": "mfa_pending"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)


def decode_token(token: str, expected_scope: str = "access") -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    if payload.get("scope") != expected_scope:
        raise HTTPException(status_code=401, detail="Token com escopo incorreto")
    return payload


def get_current_user(
    token: str = Depends(oauth2_scheme),
    _credentials=Depends(bearer_scheme),
) -> TokenData:
    payload = decode_token(token, expected_scope="access")
    return TokenData(id=payload["id"], username=payload["sub"], role=Role(payload["role"]))


def require_role(*allowed_roles: Role):
    def checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Acesso negado para este papel")
        return current_user
    return checker


def create_client_token(client_id: str, scopes: list[str]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=M2M_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": client_id,
        "scope": " ".join(scopes),
        "type": "client_credentials",
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)


def get_current_client(
    token: str = Depends(oauth2_scheme),
    _credentials=Depends(bearer_scheme),
) -> ClientTokenData:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    if payload.get("type") != "client_credentials":
        raise HTTPException(status_code=401, detail="Token não é do tipo client_credentials")
    scopes = payload.get("scope", "").split()
    return ClientTokenData(client_id=payload["sub"], scopes=scopes)


def require_scope(required_scope: str):
    def checker(current_client: ClientTokenData = Depends(get_current_client)) -> ClientTokenData:
        if required_scope not in current_client.scopes:
            raise HTTPException(status_code=403, detail=f"Escopo necessário ausente: {required_scope}")
        return current_client
    return checker