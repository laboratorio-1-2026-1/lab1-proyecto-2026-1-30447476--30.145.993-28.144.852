from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.models import ProductoTienda
from app.schemas.schemas import ProductoCreate


class ProductoRepository:

    @staticmethod
    def get_all(
        db: Session,
        solo_activos: bool = True,
        categoria_id: Optional[int] = None,
    ) -> List[ProductoTienda]:
        q = db.query(ProductoTienda)
        if solo_activos:
            q = q.filter(ProductoTienda.activo == True)
        if categoria_id is not None:
            q = q.filter(ProductoTienda.categoriaProducto_id == categoria_id)
        return q.order_by(ProductoTienda.nombre).all()

    @staticmethod
    def get_by_id(db: Session, producto_id: int) -> Optional[ProductoTienda]:
        return db.query(ProductoTienda).filter(
            ProductoTienda.idProductosTienda == producto_id
        ).first()

    @staticmethod
    def get_by_codigo_barra(db: Session, codigo: str) -> Optional[ProductoTienda]:
        return db.query(ProductoTienda).filter(
            ProductoTienda.codigoBarra == codigo
        ).first()

    @staticmethod
    def create(db: Session, data: ProductoCreate) -> ProductoTienda:
        producto = ProductoTienda(
            nombre=data.nombre,
            descripcion=data.descripcion,
            categoriaProducto_id=data.categoriaProducto_id,
            precio=data.precio,
            stock=data.stock,
            codigoBarra=data.codigoBarra,
        )
        db.add(producto)
        db.commit()
        db.refresh(producto)
        return producto

    @staticmethod
    def update_stock(db: Session, producto_id: int, nuevo_stock: int) -> Optional[ProductoTienda]:
        producto = ProductoRepository.get_by_id(db, producto_id)
        if not producto:
            return None
        producto.stock = nuevo_stock
        db.commit()
        db.refresh(producto)
        return producto

    @staticmethod
    def descontar_stock(db: Session, producto_id: int, cantidad: int) -> Optional[ProductoTienda]:
        """Descuenta `cantidad` unidades del stock. Retorna None si no hay suficiente stock."""
        producto = ProductoRepository.get_by_id(db, producto_id)
        if not producto:
            return None
        if producto.stock < cantidad:
            return None  # stock insuficiente — el servicio lanza el 409
        producto.stock -= cantidad
        db.commit()
        db.refresh(producto)
        return producto

    @staticmethod
    def desactivar(db: Session, producto_id: int) -> Optional[ProductoTienda]:
        producto = ProductoRepository.get_by_id(db, producto_id)
        if not producto:
            return None
        producto.activo = False
        db.commit()
        db.refresh(producto)
        return producto

    @staticmethod
    def tiene_stock_suficiente(db: Session, producto_id: int, cantidad: int) -> bool:
        producto = ProductoRepository.get_by_id(db, producto_id)
        if not producto or not producto.activo:
            return False
        return producto.stock >= cantidad 
