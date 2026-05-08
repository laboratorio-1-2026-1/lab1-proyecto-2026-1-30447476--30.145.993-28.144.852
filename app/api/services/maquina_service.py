from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.maquina import EstadoMaquina
from app.repositories.maquina_repository import MaquinaRepository
from app.schemas.maquina import MaquinaCreate, MaquinaUpdate

class MaquinaService:
    def __init__(self, db: Session):
        self.repo = MaquinaRepository(db)

    def crear(self, data: MaquinaCreate):
        existente = self.repo.db.query(self.repo.model).filter(self.repo.model.nombre == data.nombre).first()
        if existente:
            raise HTTPException(400, "Ya existe una máquina con ese nombre")
        return self.repo.create(**data.dict())

    def listar(self, categoria: str = None, estado: str = None):
        query = self.repo.db.query(self.repo.model)
        if categoria:
            query = query.filter(self.repo.model.categoria == categoria)
        if estado:
            query = query.filter(self.repo.model.estado == estado)
        return query.all()

    def obtener(self, id: int):
        maq = self.repo.get(id)
        if not maq:
            raise HTTPException(404, "Máquina no encontrada")
        return maq

    def actualizar(self, id: int, data: MaquinaUpdate):
        self.obtener(id)
        return self.repo.update(id, **data.dict(exclude_unset=True))

    def eliminar(self, id: int):
        if not self.repo.delete(id):
            raise HTTPException(404, "Máquina no encontrada")
        return {"mensaje": "Máquina eliminada"}

    def cambiar_estado(self, id: int, nuevo_estado: EstadoMaquina):
        self.obtener(id)
        return self.repo.update(id, estado=nuevo_estado)