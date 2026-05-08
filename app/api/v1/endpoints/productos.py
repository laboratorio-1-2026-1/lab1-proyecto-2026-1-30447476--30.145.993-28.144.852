from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import require_roles
from app.core.errors import conflict_response, bad_request_response
from app.schemas.schemas import (
    ProductoCreate,
    ProductoStockUpdate,
    ProductoOut,
)
from app.repositories.producto_repository import ProductoRepository
from app.repositories.categoria_producto_repository import CategoriaProductoRepository

router = APIRouter(prefix="/api/v1/tienda", tags=["Tienda (POS)"])


@router.get(
    "/productos",
    response_model=List[ProductoOut],
    summary="Listar productos y stock actual",
)
def listar_productos(
    categoria_id: Optional[int] = None,
    solo_activos: bool = True,
    db: Session = Depends(get_db),
    _=Depends(require_roles("Administrador", "Finanzas", "Entrenador")),
):
    return ProductoRepository.get_all(db, solo_activos=solo_activos, categoria_id=categoria_id)


@router.post(
    "/productos",
    response_model=ProductoOut,
    status_code=201,
    summary="Agregar nuevo producto al catálogo",
)
def crear_producto(
    data: ProductoCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("Administrador")),
):
    # Validar categoría si se indica
    if data.categoriaProducto_id:
        if not CategoriaProductoRepository.get_by_id(db, data.categoriaProducto_id):
            raise HTTPException(status_code=404, detail="Categoría de producto no encontrada")

    # Validar código de barra único
    if data.codigoBarra and ProductoRepository.get_by_codigo_barra(db, data.codigoBarra):
        return conflict_response(
            "ERR_CODIGO_BARRA_DUPLICADO",
            f"Ya existe un producto con el código de barra '{data.codigoBarra}'.",
        )

    if data.stock < 0:
        return bad_request_response(
            "ERR_STOCK_NEGATIVO",
            "El stock inicial no puede ser negativo.",
        )

    return ProductoRepository.create(db, data)


@router.get(
    "/productos/{producto_id}",
    response_model=ProductoOut,
    summary="Obtener detalle de un producto",
)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles("Administrador", "Finanzas", "Entrenador", "Cliente")),
):
    producto = ProductoRepository.get_by_id(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.patch(
    "/productos/{producto_id}/stock",
    response_model=ProductoOut,
    summary="Ajuste manual de inventario",
)
def ajustar_stock(
    producto_id: int,
    data: ProductoStockUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("Administrador", "Finanzas")),
):
    if data.stock < 0:
        return bad_request_response(
            "ERR_STOCK_NEGATIVO",
            "El stock no puede ser un valor negativo.",
        )

    producto = ProductoRepository.update_stock(db, producto_id, data.stock)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.delete(
    "/productos/{producto_id}",
    status_code=200,
    summary="Desactivar producto del catálogo",
)
def desactivar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles("Administrador")),
):
    producto = ProductoRepository.desactivar(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"status": "success", "mensaje": "Producto desactivado correctamente."}

    