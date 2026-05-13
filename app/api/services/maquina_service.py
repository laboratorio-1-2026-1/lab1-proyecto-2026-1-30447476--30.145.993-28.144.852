from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone
from app.api.models.maquina import EstadoMaquina
from app.api.repositories.maquina_repository import MaquinaRepository
from app.api.schemas.maquina import MaquinaCreate, MaquinaUpdate

class MaquinaService:
    def __init__(self, db: Session):
        self.repo = MaquinaRepository(db)

    def crear(self, data: MaquinaCreate):
        # Verificar regla de negocio: nombre único
        existente = self.repo.db.query(self.repo.model).filter(
            self.repo.model.nombre == data.nombre
        ).first()
        
        if existente:
            # Usar HTTP 409 para conflictos de reglas de negocio
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Conflict",
                    "codigoInterno": "ERR_NOMBRE_DUPLICADO",
                    "mensaje": f"Ya existe una máquina con el nombre '{data.nombre}'.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Crear el recurso
        maquina_creada = self.repo.create(**data.dict())
        
        # Retornar respuesta exitosa con formato HTTP 201
        return {
            "status": "success",
            "mensaje": "Máquina creada exitosamente.",
            "data": {
                "id": maquina_creada.id,
                "nombre": maquina_creada.nombre,
                "categoria": maquina_creada.categoria,
                "estado": maquina_creada.estado,
                "created_at": maquina_creada.created_at.isoformat() if maquina_creada.created_at else None
            }
        }

    def listar(self, categoria: str = None, estado: str = None):
        query = self.repo.db.query(self.repo.model)
        if categoria:
            query = query.filter(self.repo.model.categoria == categoria)
        if estado:
            query = query.filter(self.repo.model.estado == estado)
        
        maquinas = query.all()
        
        # Formato de respuesta estandarizado para listados
        return {
            "status": "success",
            "mensaje": f"Se encontraron {len(maquinas)} máquinas.",
            "data": [
                {
                    "id": m.id,
                    "nombre": m.nombre,
                    "categoria": m.categoria,
                    "estado": m.estado
                }
                for m in maquinas
            ]
        }

    def obtener(self, id: int):
        maquina = self.repo.get(id)
        if not maquina:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Not Found",
                    "codigoInterno": "ERR_RECURSO_NO_ENCONTRADO",
                    "mensaje": f"Máquina con ID {id} no encontrada.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        return {
            "status": "success",
            "mensaje": "Máquina encontrada.",
            "data": {
                "id": maquina.id,
                "nombre": maquina.nombre,
                "categoria": maquina.categoria,
                "estado": maquina.estado,
                "created_at": maquina.created_at.isoformat() if maquina.created_at else None,
                "updated_at": maquina.updated_at.isoformat() if maquina.updated_at else None
            }
        }

    def actualizar(self, id: int, data: MaquinaUpdate):
        # Verificar si existe
        maquina_existente = self.repo.get(id)
        if not maquina_existente:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Not Found",
                    "codigoInterno": "ERR_RECURSO_NO_ENCONTRADO",
                    "mensaje": f"Máquina con ID {id} no encontrada.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Verificar regla de negocio si se actualiza el nombre
        if data.nombre and data.nombre != maquina_existente.nombre:
            duplicado = self.repo.db.query(self.repo.model).filter(
                self.repo.model.nombre == data.nombre
            ).first()
            
            if duplicado:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error": "Conflict",
                        "codigoInterno": "ERR_NOMBRE_DUPLICADO",
                        "mensaje": f"Ya existe una máquina con el nombre '{data.nombre}'.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # Actualizar
        maquina_actualizada = self.repo.update(id, **data.dict(exclude_unset=True))
        
        return {
            "status": "success",
            "mensaje": "Máquina actualizada exitosamente.",
            "data": {
                "id": maquina_actualizada.id,
                "nombre": maquina_actualizada.nombre,
                "categoria": maquina_actualizada.categoria,
                "estado": maquina_actualizada.estado,
                "updated_at": maquina_actualizada.updated_at.isoformat() if maquina_actualizada.updated_at else None
            }
        }

    def eliminar(self, id: int):
        if not self.repo.delete(id):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Not Found",
                    "codigoInterno": "ERR_RECURSO_NO_ENCONTRADO",
                    "mensaje": f"Máquina con ID {id} no encontrada.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        return {
            "status": "success",
            "mensaje": "Máquina eliminada exitosamente.",
            "data": None
        }

    def cambiar_estado(self, id: int, nuevo_estado: EstadoMaquina):
        # Verificar si existe
        maquina_existente = self.repo.get(id)
        if not maquina_existente:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Not Found",
                    "codigoInterno": "ERR_RECURSO_NO_ENCONTRADO",
                    "mensaje": f"Máquina con ID {id} no encontrada.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        
        maquina_actualizada = self.repo.update(id, estado=nuevo_estado)
        
        return {
            "status": "success",
            "mensaje": f"Estado de la máquina actualizado a '{nuevo_estado.value}' exitosamente.",
            "data": {
                "id": maquina_actualizada.id,
                "nombre": maquina_actualizada.nombre,
                "estado_anterior": maquina_existente.estado,
                "estado_nuevo": nuevo_estado,
                "updated_at": maquina_actualizada.updated_at.isoformat() if maquina_actualizada.updated_at else None
            }
        }