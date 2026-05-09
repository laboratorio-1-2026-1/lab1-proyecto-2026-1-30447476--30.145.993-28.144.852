from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone
from app.models.maquina import EstadoMaquina
from app.repositories.ticketsMantenimiento_repository import TicketMantenimientoRepository
from app.services.maquina_service import MaquinaService
from app.schemas.ticketsMantenimiento import TicketCreate, TicketResolve


class MantenimientoService:
    def __init__(self, db: Session):
        self.repo = TicketMantenimientoRepository(db)
        self.maquina_service = MaquinaService(db)

    def abrir_ticket(self, maquina_id: int, data: TicketCreate):
        # Verificar si la máquina existe
        try:
            maquina = self.maquina_service.obtener(maquina_id)
        except HTTPException as e:
            if e.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "Not Found",
                        "codigoInterno": "ERR_MAQUINA_NO_ENCONTRADA",
                        "mensaje": f"Máquina con ID {maquina_id} no encontrada.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            raise e

        # Verificar regla de negocio: No abrir ticket si ya hay uno abierto
        ticket_abierto = self.repo.get_abiertos_by_maquina(maquina_id)
        if ticket_abierto:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Conflict",
                    "codigoInterno": "ERR_TICKET_ABIERTO_EXISTENTE",
                    "mensaje": f"La máquina con ID {maquina_id} ya tiene un ticket de mantenimiento abierto. Debe resolverlo antes de crear uno nuevo.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )

        # Crear el ticket
        ticket = self.repo.create(
            maquina_id=maquina_id,
            usuario_id=data.usuario_id if hasattr(data, 'usuario_id') else None,
            descripcion_falla=data.descripcion_falla,
            tecnico_responsable=data.tecnico_responsable if hasattr(data, 'tecnico_responsable') else None,
            costo_reparacion=data.costo_reparacion if hasattr(data, 'costo_reparacion') else None
        )

        # Cambiar estado de la máquina si está activa
        if maquina.get("data", {}).get("estado") == EstadoMaquina.ACTIVA:
            self.maquina_service.cambiar_estado(maquina_id, EstadoMaquina.EN_MANTENIMIENTO)

        # Retornar respuesta exitosa
        return {
            "status": "success",
            "mensaje": "Ticket de mantenimiento creado exitosamente.",
            "data": {
                "id": ticket.id,
                "maquina_id": ticket.maquina_id,
                "descripcion_falla": ticket.descripcionFalla if hasattr(ticket, 'descripcionFalla') else ticket.descripcion_falla if hasattr(ticket, 'descripcion_falla') else None,
                "estado": ticket.estado,
                "costo_reparacion": float(ticket.costoReparacion) if hasattr(ticket, 'costoReparacion') and ticket.costoReparacion else float(ticket.costo_reparacion) if hasattr(ticket, 'costo_reparacion') and ticket.costo_reparacion else None,
                "fecha_apertura": ticket.fechaReporte.isoformat() if hasattr(ticket, 'fechaReporte') and ticket.fechaReporte else ticket.fecha_apertura.isoformat() if hasattr(ticket, 'fecha_apertura') and ticket.fecha_apertura else None,
                "fecha_resolucion": None
            }
        }

    def listar_por_maquina(self, maquina_id: int):
        # Verificar si la máquina existe
        try:
            self.maquina_service.obtener(maquina_id)
        except HTTPException as e:
            if e.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "Not Found",
                        "codigoInterno": "ERR_MAQUINA_NO_ENCONTRADA",
                        "mensaje": f"Máquina con ID {maquina_id} no encontrada.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            raise e

        tickets = self.repo.get_by_maquina(maquina_id)

        # Formato de respuesta estandarizado para listados
        return {
            "status": "success",
            "mensaje": f"Se encontraron {len(tickets)} tickets de mantenimiento para la máquina ID {maquina_id}.",
            "data": [
                {
                    "id": t.id,
                    "descripcion_falla": t.descripcionFalla if hasattr(t, 'descripcionFalla') else t.descripcion_falla if hasattr(t, 'descripcion_falla') else None,
                    "estado": t.estado,
                    "costo_reparacion": float(t.costoReparacion) if hasattr(t, 'costoReparacion') and t.costoReparacion else float(t.costo_reparacion) if hasattr(t, 'costo_reparacion') and t.costo_reparacion else None,
                    "fecha_apertura": t.fechaReporte.isoformat() if hasattr(t, 'fechaReporte') and t.fechaReporte else t.fecha_apertura.isoformat() if hasattr(t, 'fecha_apertura') and t.fecha_apertura else None,
                    "fecha_resolucion": t.fechaResolucion.isoformat() if hasattr(t, 'fechaResolucion') and t.fechaResolucion else t.fecha_resolucion.isoformat() if hasattr(t, 'fecha_resolucion') and t.fecha_resolucion else None
                }
                for t in tickets
            ]
        }

    def obtener_ticket(self, ticket_id: int):
        # Verificar si el ticket existe
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Not Found",
                    "codigoInterno": "ERR_TICKET_NO_ENCONTRADO",
                    "mensaje": f"Ticket de mantenimiento con ID {ticket_id} no encontrado.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )

        return {
            "status": "success",
            "mensaje": "Ticket de mantenimiento encontrado.",
            "data": {
                "id": ticket.id,
                "maquina_id": ticket.maquina_id,
                "descripcion_falla": ticket.descripcionFalla if hasattr(ticket, 'descripcionFalla') else ticket.descripcion_falla if hasattr(ticket, 'descripcion_falla') else None,
                "estado": ticket.estado,
                "costo_reparacion": float(ticket.costoReparacion) if hasattr(ticket, 'costoReparacion') and ticket.costoReparacion else float(ticket.costo_reparacion) if hasattr(ticket, 'costo_reparacion') and ticket.costo_reparacion else None,
                "fecha_apertura": ticket.fechaReporte.isoformat() if hasattr(ticket, 'fechaReporte') and ticket.fechaReporte else ticket.fecha_apertura.isoformat() if hasattr(ticket, 'fecha_apertura') and ticket.fecha_apertura else None,
                "fecha_resolucion": ticket.fechaResolucion.isoformat() if hasattr(ticket, 'fechaResolucion') and ticket.fechaResolucion else ticket.fecha_resolucion.isoformat() if hasattr(ticket, 'fecha_resolucion') and ticket.fecha_resolucion else None
            }
        }

    def resolver_ticket(self, ticket_id: int, data: TicketResolve):
        # Verificar si el ticket existe
        ticket = self.repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Not Found",
                    "codigoInterno": "ERR_TICKET_NO_ENCONTRADO",
                    "mensaje": f"Ticket de mantenimiento con ID {ticket_id} no encontrado.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )

        # Verificar regla de negocio: No resolver ticket ya cerrado
        if ticket.estado == "Cerrado":
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Conflict",
                    "codigoInterno": "ERR_TICKET_YA_CERRADO",
                    "mensaje": f"El ticket con ID {ticket_id} ya se encuentra cerrado. No se puede resolver nuevamente.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )

        # Resolver el ticket usando el método resolver del repositorio
        ticket_actualizado = self.repo.resolver(
            ticket_id=ticket_id,
            costo_reparacion=data.costo_reparacion if hasattr(data, 'costo_reparacion') else None,
            tecnico_responsable=data.tecnico_responsable if hasattr(data, 'tecnico_responsable') else None
        )

        if not ticket_actualizado:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Not Found",
                    "codigoInterno": "ERR_TICKET_NO_ENCONTRADO",
                    "mensaje": f"Ticket de mantenimiento con ID {ticket_id} no encontrado.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )

        # Verificar si hay otros tickets abiertos para esta máquina
        tickets_abiertos = self.repo.count_abiertos_by_maquina(ticket.maquina_id)

        # Si no hay más tickets abiertos, cambiar estado de la máquina a ACTIVA
        if tickets_abiertos == 0:
            self.maquina_service.cambiar_estado(ticket.maquina_id, EstadoMaquina.ACTIVA)

        # Retornar respuesta exitosa
        return {
            "status": "success",
            "mensaje": "Ticket de mantenimiento resuelto exitosamente.",
            "data": {
                "id": ticket_actualizado.id,
                "maquina_id": ticket_actualizado.maquina_id,
                "estado": ticket_actualizado.estado,
                "costo_reparacion": float(ticket_actualizado.costoReparacion) if hasattr(ticket_actualizado, 'costoReparacion') and ticket_actualizado.costoReparacion else float(ticket_actualizado.costo_reparacion) if hasattr(ticket_actualizado, 'costo_reparacion') and ticket_actualizado.costo_reparacion else None,
                "fecha_apertura": ticket_actualizado.fechaReporte.isoformat() if hasattr(ticket_actualizado, 'fechaReporte') and ticket_actualizado.fechaReporte else ticket_actualizado.fecha_apertura.isoformat() if hasattr(ticket_actualizado, 'fecha_apertura') and ticket_actualizado.fecha_apertura else None,
                "fecha_resolucion": datetime.now(timezone.utc).isoformat()
            }
        }