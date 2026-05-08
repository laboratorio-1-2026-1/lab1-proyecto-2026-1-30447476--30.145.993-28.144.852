from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, List
from app.repositories.producto_repository import ProductoRepository
from app.repositories.categoria_producto_repository import CategoriaProductoRepository
from app.schemas.producto import ProductoCreate, ProductoUpdate
from app.models.producto import Producto

class ProductoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductoRepository(db)
        self.cat_repo = CategoriaProductoRepository(db)

    def crear(self, data: ProductoCreate) -> Producto:
        # Validar que la categoría exista
        categoria = self.cat_repo.get(data.categoria_producto_id)
        if not categoria:
            raise HTTPException(status_code=400, detail="Categoría de producto no válida")
        
        # Validar código de barras único
        if data.codigo_barra:
            existente = self.repo.db.query(self.repo.model).filter(
                self.repo.model.codigo_barra == data.codigo_barra
            ).first()
            if existente:
                raise HTTPException(status_code=400, detail="Ya existe un producto con ese código de barras")
        
        return self.repo.create(**data.dict())

    def listar(self, activo: Optional[bool] = None, skip: int = 0, limit: int = 100) -> List[Producto]:
        query = self.repo.db.query(self.repo.model)
        if activo is not None:
            query = query.filter(self.repo.model.activo == activo)
        return query.offset(skip).limit(limit).all()

    def obtener(self, producto_id: int) -> Producto:
        producto = self.repo.get(producto_id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return producto

    def actualizar(self, producto_id: int, data: ProductoUpdate) -> Producto:
        # Verificar existencia
        self.obtener(producto_id)
        
        # Validar código de barras único si se está actualizando
        if data.codigo_barra:
            existente = self.repo.db.query(self.repo.model).filter(
                self.repo.model.codigo_barra == data.codigo_barra,
                self.repo.model.id != producto_id
            ).first()
            if existente:
                raise HTTPException(status_code=400, detail="El código de barras ya está en uso")
        
        # Validar categoría si se actualiza
        if data.categoria_producto_id:
            categoria = self.cat_repo.get(data.categoria_producto_id)
            if not categoria:
                raise HTTPException(status_code=400, detail="Categoría de producto no válida")
        
        updated = self.repo.update(producto_id, **data.dict(exclude_unset=True))
        return updated

    def eliminar(self, producto_id: int) -> None:
        if not self.repo.delete(producto_id):
            raise HTTPException(status_code=404, detail="Producto no encontrado")