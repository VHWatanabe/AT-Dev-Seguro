from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.auth.security import require_role
from app.models.user import Role
from app.models.consulta import Consulta
from app.database.database import get_session

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/relatorio")
def relatorio_completo(
    current_user=Depends(require_role(Role.administrador)),
    session: Session = Depends(get_session),
):
    return session.exec(select(Consulta)).all()