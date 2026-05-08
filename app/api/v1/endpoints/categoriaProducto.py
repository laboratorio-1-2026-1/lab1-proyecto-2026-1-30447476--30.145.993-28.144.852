from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, require_roles
from app.schemas.categorias_productos import (
    CategoriaProductoCreate,
    CategoriaProductoUpdate,
    CategoriaProductoResponse,
)
from app.repositories.categorias_productos_repository import CategoriaProductoRepository

router = APIRouter(prefix="/categorias-productos", tags=["Categorías de Productos"])


@router.post(
    "/",
    response_model=CategoriaProductoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva categoría de producto",
)
def crear_categoria(
    data: CategoriaProductoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Administrador")),
):
    """
    Crea una nueva categoría de producto.
    Solo accesible por Administradores.
    """
    # Validar que no exista una categoría con el mismo nombre
    existing = CategoriaProductoRepository.get_by_nombre(db, data.nombre)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una categoría con el nombre '{data.nombre}'.",
        )

    return CategoriaProductoRepository.create(db, data)


@router.get(
    "/",
    response_model=List[CategoriaProductoResponse],
    summary="Listar todas las categorías de productos",
)
def listar_categorias(
    db: Session = Depends(get_db),
    _=Depends(require_roles("Administrador", "Finanzas")),
):
    """
    Obtiene el listado completo de categorías de productos.
    Accesible por múltiples roles (Administrador, Finanzas).
    """
    return CategoriaProductoRepository.get_all(db)


@router.get(
    "/{categoria_id}",
    response_model=CategoriaProductoResponse,
    summary="Obtener una categoría por su ID",
)
def obtener_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles("Administrador", "Finanzas")),
):
    """
    Devuelve los datos de una categoría específica.
    """
    categoria = CategoriaProductoRepository.get_by_id(db, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada.",
        )
    return categoria


@router.put(
    "/{categoria_id}",
    response_model=CategoriaProductoResponse,
    summary="Actualizar completamente una categoría (reemplazo total)",
)
def actualizar_categoria(
    categoria_id: int,
    data: CategoriaProductoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Administrador")),
):
    """
    Actualiza todos los campos de una categoría. Los campos no enviados se consideran nulos (reemplazo completo).
    """
    categoria = CategoriaProductoRepository.get_by_id(db, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada.",
        )

    # Si se cambia el nombre, verificar que no exista otro con ese nombre (excepto el mismo)
    if data.nombre and data.nombre != categoria.nombre:
        existing = CategoriaProductoRepository.get_by_nombre(db, data.nombre)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otra categoría con el nombre '{data.nombre}'.",
            )

    return CategoriaProductoRepository.update(db, categoria_id, data)


@router.patch(
    "/{categoria_id}",
    response_model=CategoriaProductoResponse,
    summary="Actualizar parcialmente una categoría",
)
def actualizar_categoria_parcial(
    categoria_id: int,
    data: CategoriaProductoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Administrador")),
):
    """
    Actualiza solo los campos enviados de una categoría (actualización parcial).
    """
    categoria = CategoriaProductoRepository.get_by_id(db, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada.",
        )

    # Validar unicidad del nombre solo si se envía y cambia
    if data.nombre is not None and data.nombre != categoria.nombre:
        existing = CategoriaProductoRepository.get_by_nombre(db, data.nombre)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otra categoría con el nombre '{data.nombre}'.",
            )

    return CategoriaProductoRepository.update(db, categoria_id, data)


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una categoría",
)
def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Administrador")),
):
    """
    Elimina una categoría de productos.
    Solo administradores.
    Nota: Si la categoría tiene productos asociados, se impide la eliminación.
    """
    categoria = CategoriaProductoRepository.get_by_id(db, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada.",
        )

    # Verificar si hay productos usando esta categoría
    productos_asociados = CategoriaProductoRepository.count_associated_products(db, categoria_id)
    if productos_asociados > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar la categoría porque tiene {productos_asociados} producto(s) asociado(s). Reasigne o elimine los productos primero.",
        )

    CategoriaProductoRepository.delete(db, categoria_id)
    return None  # 204 No Content