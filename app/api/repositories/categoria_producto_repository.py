from typing import List, Optional
from sqlalchemy.orm import Session

from app.api.models.models import CategoriaProducto
from app.api.schemas.schemas import ProductoCreate


class CategoriaProductoRepository:

    @staticmethod
    def get_all(db: Session) -> List[CategoriaProducto]:
        return db.query(CategoriaProducto).order_by(CategoriaProducto.idCategoriasProductos).all()

    @staticmethod
    def get_by_id(db: Session, categoria_id: int) -> Optional[CategoriaProducto]:
        return db.query(CategoriaProducto).filter(
            CategoriaProducto.idCategoriasProductos == categoria_id
        ).first()

    @staticmethod
    def get_by_nombre(db: Session, nombre: str) -> Optional[CategoriaProducto]:
        return db.query(CategoriaProducto).filter(
            CategoriaProducto.nombre == nombre
        ).first()

    @staticmethod
    def create(db: Session, nombre: str, descripcion: Optional[str] = None) -> CategoriaProducto:
        categoria = CategoriaProducto(nombre=nombre, descripcion=descripcion)
        db.add(categoria)
        db.commit()
        db.refresh(categoria)
        return categoria

    @staticmethod
    def update(
        db: Session, categoria_id: int, nombre: Optional[str] = None, descripcion: Optional[str] = None
    ) -> Optional[CategoriaProducto]:
        categoria = CategoriaProductoRepository.get_by_id(db, categoria_id)
        if not categoria:
            return None
        if nombre is not None:
            categoria.nombre = nombre
        if descripcion is not None:
            categoria.descripcion = descripcion
        db.commit()
        db.refresh(categoria)
        return categoria

    @staticmethod
    def delete(db: Session, categoria_id: int) -> bool:
        categoria = CategoriaProductoRepository.get_by_id(db, categoria_id)
        if not categoria:
            return False
        db.delete(categoria)
        db.commit()
        return True 