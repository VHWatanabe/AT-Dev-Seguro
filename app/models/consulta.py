from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import ConfigDict, NaiveDatetime


class StatusConsulta(str, Enum):
    agendada = "agendada"
    confirmada = "confirmada"
    cancelada = "cancelada"
    concluida = "concluida"


class ConsultaBase(SQLModel):
    paciente_id: int
    profissional_id: int
    data_hora: NaiveDatetime
    status: StatusConsulta = StatusConsulta.agendada


class ConsultaCreate(ConsultaBase):
    model_config = ConfigDict(extra="forbid")


class Consulta(ConsultaBase, table=True):
    """Tabela persistida no banco. Nunca deve ser retornada diretamente pela API."""
    id: Optional[int] = Field(default=None, primary_key=True)
    observacoes_internas: Optional[str] = None


class ConsultaPublic(ConsultaBase):
    """Modelo exposto na API. Não inclui campos internos de auditoria."""
    id: int