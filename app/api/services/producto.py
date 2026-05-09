from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, List
from datetime import datetime, timezone
from app.repositories.producto_repository import ProductoRepository
from app.repositories.categoria_producto_repository import CategoriaProductoRepository
from app.schemas.producto import ProductoCreate, ProductoUpdate
from app.models.producto import Producto

class ProductoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductoRepository(db)
        self.cat_repo = CategoriaProductoRepository(db)

    def crear(self, data: ProductoCreate):
        # Validar que la categoría exista (regla de negocio)
        categoria = self.cat_repo.get(data.categoria_producto_id)
        if not categoria:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Conflict",
                    "codigoInterno": "ERR_CATEGORIA_NO_VALIDA",
                    "mensaje": f"Categoría de producto con ID {data.categoria_producto_id} no válida o no existe.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Validar código de barras único (regla de negocio)
        if data.codigo_barra:
            existente = self.repo.db.query(self.repo.model).filter(
                self.repo.model.codigo_barra == data.codigo_barra
            ).first()
            if existente:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error": "Conflict",
                        "codigoInterno": "ERR_CODIGO_BARRAS_DUPLICADO",
                        "mensaje": f"Ya existe un producto con el código de barras '{data.codigo_barra}'.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # Crear el producto
        producto_creado = self.repo.create(**data.dict())
        
        # Retornar respuesta exitosa con código HTTP 201
        return {
            "status": "success",
            "mensaje": "Producto creado exitosamente.",
            "data": {
                "id": producto_creado.id,
                "nombre": producto_creado.nombre,
                "codigo_barra": producto_creado.codigo_barra,
                "categoria_producto_id": producto_creado.categoria_producto_id,
                "activo": producto_creado.activo,
                "created_at": producto_creado.created_at.isoformat() if hasattr(producto_creado, 'created_at') and producto_creado.created_at else None
            }
        }

    def listar(self, activo: Optional[bool] = None, skip: int = 0, limit: int = 100):
        query = self.repo.db.query(self.repo.model)
        if activo is not None:
            query = query.filter(self.repo.model.activo == activo)
        
        productos = query.offset(skip).limit(limit).all()
        
        # Formato de respuesta estandarizado para listados
        return {
            "status": "success",
            "mensaje": f"Se encontraron {len(productos)} productos.",
            "data": [
                {
                    "id": p.id,
                    "nombre": p.nombre,
                    "codigo_barra": p.codigo_barra,
                    "categoria_producto_id": p.categoria_producto_id,
                    "activo": p.activo,
                    "precio": float(p.precio) if hasattr(p, 'precio') and p.precio else None,
                    "stock": p.stock if hasattr(p, 'stock') else None
                }
                for p in productos
            ]
        }

    def obtener(self, producto_id: int):
        producto = self.repo.get(producto_id)
        if not producto:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Not Found",
                    "codigoInterno": "ERR_PRODUCTO_NO_ENCONTRADO",
                    "mensaje": f"Producto con ID {producto_id} no encontrado.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        return {
            "status": "success",
            "mensaje": "Producto encontrado.",
            "data": {
                "id": producto.id,
                "nombre": producto.nombre,
                "descripcion": producto.descripcion if hasattr(producto, 'descripcion') else None,
                "codigo_barra": producto.codigo_barra,
                "categoria_producto_id": producto.categoria_producto_id,
                "activo": producto.activo,
                "precio": float(producto.precio) if hasattr(producto, 'precio') and producto.precio else None,
                "stock": producto.stock if hasattr(producto, 'stock') else None,
                "created_at": producto.created_at.isoformat() if hasattr(producto, 'created_at') and producto.created_at else None,
                "updated_at": producto.updated_at.isoformat() if hasattr(producto, 'updated_at') and producto.updated_at else None
            }
        }

    def actualizar(self, producto_id: int, data: ProductoUpdate):
        # Verificar existencia
        try:
            producto_existente = self.obtener(producto_id)
        except HTTPException as e:
            if e.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "Not Found",
                        "codigoInterno": "ERR_PRODUCTO_NO_ENCONTRADO",
                        "mensaje": f"Producto con ID {producto_id} no encontrado.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            raise e
        
        # Validar código de barras único si se está actualizando (regla de negocio)
        if data.codigo_barra:
            existente = self.repo.db.query(self.repo.model).filter(
                self.repo.model.codigo_barra == data.codigo_barra,
                self.repo.model.id != producto_id
            ).first()
            if existente:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error": "Conflict",
                        "codigoInterno": "ERR_CODIGO_BARRAS_DUPLICADO",
                        "mensaje": f"El código de barras '{data.codigo_barra}' ya está en uso por otro producto.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # Validar categoría si se actualiza (regla de negocio)
        if data.categoria_producto_id:
            categoria = self.cat_repo.get(data.categoria_producto_id)
            if not categoria:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error": "Conflict",
                        "codigoInterno": "ERR_CATEGORIA_NO_VALIDA",
                        "mensaje": f"Categoría de producto con ID {data.categoria_producto_id} no válida o no existe.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # Actualizar el producto
        producto_actualizado = self.repo.update(producto_id, **data.dict(exclude_unset=True))
        
        return {
            "status": "success",
            "mensaje": "Producto actualizado exitosamente.",
            "data": {
                "id": producto_actualizado.id,
                "nombre": producto_actualizado.nombre,
                "codigo_barra": producto_actualizado.codigo_barra,
                "categoria_producto_id": producto_actualizado.categoria_producto_id,
                "activo": producto_actualizado.activo,
                "precio": float(producto_actualizado.precio) if hasattr(producto_actualizado, 'precio') and producto_actualizado.precio else None,
                "stock": producto_actualizado.stock if hasattr(producto_actualizado, 'stock') else None,
                "updated_at": producto_actualizado.updated_at.isoformat() if hasattr(producto_actualizado, 'updated_at') and producto_actualizado.updated_at else None
            }
        }

    def eliminar(self, producto_id: int):
        # Verificar existencia antes de eliminar
        try:
            self.obtener(producto_id)
        except HTTPException as e:
            if e.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "Not Found",
                        "codigoInterno": "ERR_PRODUCTO_NO_ENCONTRADO",
                        "mensaje": f"Producto con ID {producto_id} no encontrado.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            raise e
        
        # Verificar regla de negocio: No eliminar producto si tiene ventas asociadas
        # (Agrega esta validación si tu modelo tiene relación con ventas)
        # if hasattr(self.repo.model, 'ventas') and self.repo.model.ventas:
        #     raise HTTPException(
        #         status_code=409,
        #         detail={
        #             "error": "Conflict",
        #             "codigoInterno": "ERR_PRODUCTO_CON_VENTAS",
        #             "mensaje": f"No se puede eliminar el producto con ID {producto_id} porque tiene ventas asociadas.",
        #             "timestamp": datetime.now(timezone.utc).isoformat()
        #         }
        #     )
        
        # Realizar eliminación lógica o física
        if not self.repo.delete(producto_id):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Not Found",
                    "codigoInterno": "ERR_PRODUCTO_NO_ENCONTRADO",
                    "mensaje": f"Producto con ID {producto_id} no encontrado.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        return {
            "status": "success",
            "mensaje": "Producto eliminado exitosamente.",
            "data": None
        }