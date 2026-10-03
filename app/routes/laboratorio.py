from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from app.auth.security import require_scope
from app.models.consulta import Consulta
from app.database.database import get_session

router = APIRouter(prefix="/laboratorio", tags=["laboratorio"])


@router.get("/horarios-ocupados")
def horarios_ocupados(
    profissional_id: int = Query(...),
    current_client=Depends(require_scope("laboratorio:horarios:leitura")),
    session: Session = Depends(get_session),
):
    statement = select(Consulta).where(Consulta.profissional_id == profissional_id)
    consultas = session.exec(statement).all()
    return {
        "profissional_id": profissional_id,
        "horarios_ocupados": [c.data_hora for c in consultas],
    }