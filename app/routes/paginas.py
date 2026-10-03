from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.database.database import get_session
from app.models.consulta import Consulta

router = APIRouter(tags=["paginas"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/agenda", response_class=HTMLResponse)
def agenda_do_dia(request: Request, session: Session = Depends(get_session)):
    consultas = session.exec(select(Consulta)).all()
    return templates.TemplateResponse(
        request, "consultas_lista.html", {"consultas": consultas}
    )