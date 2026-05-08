from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import require_roles
from app.core.errors import conflict_response
from app.schemas.schemas import (
    TicketCreate,
    TicketResolverRequest,
    TicketOut,
)
from app.repositories.maquina_repository import MaquinaRepository
from app.repositories.mantenimiento_repository import MantenimientoRepository

router = APIRouter(prefix="/api/v1", tags=["Máquinas e Instalaciones"])


@router.get(
    "/maquinas/{maquina_id}/tickets",
    response_model=List[TicketOut],
    summary="Historial de tickets de mantenimiento de una máquina",
)
def listar_tickets(
    maquina_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles("Administrador")),
):
    if not MaquinaRepository.get_by_id(db, maquina_id):
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    return MantenimientoRepository.get_by_maquina(db, maquina_id)


@router.post(
    "/tickets-mantenimiento",
    response_model=TicketOut,
    status_code=201,
    summary="Abrir ticket de mantenimiento (cambia máquina a 'En Mantenimiento')",
)
def abrir_ticket(
    data: TicketCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Administrador")),
):
    if not MaquinaRepository.get_by_id(db, data.maquina_id):
        raise HTTPException(status_code=404, detail="Máquina no encontrada")

    # Aviso si ya hay un ticket abierto para esa máquina (no bloqueante, pero informativo)
    if MantenimientoRepository.exists_abierto_para_maquina(db, data.maquina_id):
        return conflict_response(
            "ERR_TICKET_YA_ABIERTO",
            "La máquina ya tiene un ticket de mantenimiento abierto.",
        )

    return MantenimientoRepository.create(
        db,
        maquina_id=data.maquina_id,
        usuario_id=current_user.idUsuarios,
        descripcion_falla=data.descripcionFalla,
        tecnico_responsable=data.tecnicoResponsable,
    )


@router.patch(
    "/tickets-mantenimiento/{ticket_id}/resolver",
    response_model=TicketOut,
    summary="Cerrar ticket y rehabilitar máquina a 'Activa'",
)
def resolver_ticket(
    ticket_id: int,
    data: TicketResolverRequest,
    db: Session = Depends(get_db),
    _=Depends(require_roles("Administrador")),
):
    ticket = MantenimientoRepository.get_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if ticket.estado == "Resuelto":
        return conflict_response(
            "ERR_TICKET_YA_RESUELTO",
            "Este ticket ya fue resuelto anteriormente.",
        )

    return MantenimientoRepository.resolver(
        db,
        ticket_id=ticket_id,
        fecha_resolucion=data.fechaResolucion,
        costo_reparacion=data.costoReparacion,
        tecnico_responsable=data.tecnicoResponsable,
    )