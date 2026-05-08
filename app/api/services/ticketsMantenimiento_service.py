from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from app.models.maquina import EstadoMaquina
from app.repositories.mantenimiento_repository import MantenimientoRepository
from app.services.maquina_service import MaquinaService
from app.schemas.mantenimiento import TicketCreate, TicketResolve

class MantenimientoService:
    def __init__(self, db: Session):
        self.repo = MantenimientoRepository(db)
        self.maquina_service = MaquinaService(db)

    def abrir_ticket(self, maquina_id: int, data: TicketCreate):
        maquina = self.maquina_service.obtener(maquina_id)
        ticket = self.repo.create(
            maquina_id=maquina_id,
            descripcion_falla=data.descripcion_falla,
            estado="Abierto",
            costo_reparacion=data.costo_reparacion
        )
        if maquina.estado == EstadoMaquina.ACTIVA:
            self.maquina_service.cambiar_estado(maquina_id, EstadoMaquina.EN_MANTENIMIENTO)
        return ticket

    def listar_por_maquina(self, maquina_id: int):
        self.maquina_service.obtener(maquina_id)
        return self.repo.db.query(self.repo.model).filter(
            self.repo.model.maquina_id == maquina_id
        ).order_by(self.repo.model.fecha_apertura.desc()).all()

    def resolver_ticket(self, ticket_id: int, data: TicketResolve):
        ticket = self.repo.get(ticket_id)
        if not ticket:
            raise HTTPException(404, "Ticket no encontrado")
        if ticket.estado == "Cerrado":
            raise HTTPException(409, "El ticket ya está cerrado")
        update_data = {"estado": "Cerrado", "fecha_resolucion": datetime.utcnow()}
        if data.costo_reparacion is not None:
            update_data["costo_reparacion"] = data.costo_reparacion
        ticket_actualizado = self.repo.update(ticket_id, **update_data)

        tickets_abiertos = self.repo.db.query(self.repo.model).filter(
            self.repo.model.maquina_id == ticket.maquina_id,
            self.repo.model.estado == "Abierto"
        ).count()
        if tickets_abiertos == 0:
            self.maquina_service.cambiar_estado(ticket.maquina_id, EstadoMaquina.ACTIVA)
        return ticket_actualizado