from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.models.consulta import Consulta, ConsultaCreate, ConsultaPublic
from app.models.user import Role, TokenData
from app.database.database import get_session
from app.auth.security import require_role, get_current_user

router = APIRouter(prefix="/consultas", tags=["consultas"])


def verificar_ownership(consulta: Consulta, current_user: TokenData):
    if current_user.role == Role.administrador:
        return
    if current_user.role == Role.profissional_saude and consulta.profissional_id == current_user.id:
        return
    raise HTTPException(status_code=403, detail="Você não tem permissão sobre este recurso")


def obter_consulta_ou_404(consulta_id: int, session: Session) -> Consulta:
    consulta = session.get(Consulta, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    return consulta


@router.post("/", response_model=ConsultaPublic, status_code=201)
def criar_consulta(
    consulta: ConsultaCreate,
    current_user: TokenData = Depends(require_role(Role.profissional_saude, Role.administrador)),
    session: Session = Depends(get_session),
):
    nova = Consulta(
        **consulta.model_dump(),
        observacoes_internas=f"Criado por {current_user.username} em {datetime.now(timezone.utc).isoformat()}",
    )
    session.add(nova)
    session.commit()
    session.refresh(nova)
    return nova


@router.get("/", response_model=list[ConsultaPublic])
def listar_consultas(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role == Role.profissional_saude:
        statement = select(Consulta).where(Consulta.profissional_id == current_user.id)
        return session.exec(statement).all()
    return session.exec(select(Consulta)).all()


@router.get("/{consulta_id}", response_model=ConsultaPublic)
def obter_consulta(
    consulta_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    consulta = obter_consulta_ou_404(consulta_id, session)
    verificar_ownership(consulta, current_user)
    return consulta


@router.put("/{consulta_id}", response_model=ConsultaPublic)
def atualizar_consulta(
    consulta_id: int,
    dados: ConsultaCreate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    existente = obter_consulta_ou_404(consulta_id, session)
    verificar_ownership(existente, current_user)
    for campo, valor in dados.model_dump().items():
        setattr(existente, campo, valor)
    session.add(existente)
    session.commit()
    session.refresh(existente)
    return existente


@router.delete("/{consulta_id}", status_code=204)
def deletar_consulta(
    consulta_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    existente = obter_consulta_ou_404(consulta_id, session)
    verificar_ownership(existente, current_user)
    session.delete(existente)
    session.commit()