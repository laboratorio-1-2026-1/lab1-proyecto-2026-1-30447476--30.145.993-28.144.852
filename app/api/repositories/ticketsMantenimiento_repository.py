from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session

from app.api.models.models import TicketMantenimiento, Maquina


class TicketMantenimientoRepository:

    @staticmethod
    def get_all(db: Session) -> List[TicketMantenimiento]:
        return db.query(TicketMantenimiento).order_by(
            TicketMantenimiento.fechaReporte.desc()
        ).all()

    @staticmethod
    def get_by_id(db: Session, ticket_id: int) -> Optional[TicketMantenimiento]:
        return db.query(TicketMantenimiento).filter(
            TicketMantenimiento.idTicketsMantenimiento == ticket_id
        ).first()

    @staticmethod
    def get_by_maquina(db: Session, maquina_id: int) -> List[TicketMantenimiento]:
        return db.query(TicketMantenimiento).filter(
            TicketMantenimiento.maquina_id == maquina_id
        ).order_by(TicketMantenimiento.fechaReporte.desc()).all()

    @staticmethod
    def get_abiertos(db: Session) -> List[TicketMantenimiento]:
        return db.query(TicketMantenimiento).filter(
            TicketMantenimiento.estado == "Abierto"
        ).order_by(TicketMantenimiento.fechaReporte.desc()).all()

    @staticmethod
    def create(
        db: Session,
        maquina_id: int,
        usuario_id: int,
        descripcion_falla: str,
        tecnico_responsable: Optional[str] = None,
    ) -> TicketMantenimiento:
        ticket = TicketMantenimiento(
            maquina_id=maquina_id,
            usuario_id=usuario_id,
            descripcionFalla=descripcion_falla,
            tecnicoResponsable=tecnico_responsable,
            estado="Abierto",
        )
        # Regla de negocio: cambiar estado de la máquina a "En Mantenimiento"
        maquina = db.query(Maquina).filter(Maquina.idMaquinas == maquina_id).first()
        if maquina:
            maquina.estadoOperativo = "En Mantenimiento"

        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def resolver(
        db: Session,
        ticket_id: int,
        fecha_resolucion: date,
        costo_reparacion: Optional[Decimal] = None,
        tecnico_responsable: Optional[str] = None,
    ) -> Optional[TicketMantenimiento]:
        ticket = TicketMantenimientoRepository.get_by_id(db, ticket_id)
        if not ticket:
            return None

        ticket.fechaResolucion = fecha_resolucion
        ticket.costoReparacion = costo_reparacion
        if tecnico_responsable:
            ticket.tecnicoResponsable = tecnico_responsable
        ticket.estado = "Resuelto"

        # Regla de negocio: rehabilitar máquina a "Activa"
        maquina = db.query(Maquina).filter(Maquina.idMaquinas == ticket.maquina_id).first()
        if maquina:
            maquina.estadoOperativo = "Activa"
            maquina.ultimoMantenimiento = fecha_resolucion

        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def exists_abierto_para_maquina(db: Session, maquina_id: int) -> bool:
        return db.query(TicketMantenimiento).filter(
            TicketMantenimiento.maquina_id == maquina_id,
            TicketMantenimiento.estado == "Abierto",
        ).first() is not None 