from app.api.repositories.venta_repository import VentaRepository
from app.api.repositories.producto_repository import ProductoRepository
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict
from datetime import datetime, timezone

class VentaService:
    def __init__(self, db: Session):
        self.venta_repo = VentaRepository(db)
        self.producto_repo = ProductoRepository(db)
        self.db = db
   
    def registrar_venta(
        self,
        cliente_id: int,
        items: List[Dict],  # [{"producto_id": 1, "cantidad": 2, "precio_unitario": 15.0}]
        metodo_pago: str
    ) -> dict:
        """
        LÓGICA CRÍTICA: Registrar venta y decrementar stock automáticamente
        """
        # Validar que todos los productos existen y hay stock
        for item in items:
            producto = self.producto_repo.read_by_id(item["producto_id"])
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "Not Found",
                        "codigoInterno": "ERR_PRODUCTO_NO_ENCONTRADO",
                        "mensaje": f"Producto con ID {item['producto_id']} no encontrado.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
           
            if producto.stock < item["cantidad"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": "Conflict",
                        "codigoInterno": "ERR_VENTA_STOCK_INSUFICIENTE",
                        "mensaje": f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}, Solicitado: {item['cantidad']}",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        # Validar regla de negocio: Método de pago válido
        metodos_validos = ["efectivo", "tarjeta", "transferencia", "credito"]
        if metodo_pago.lower() not in metodos_validos:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Conflict",
                    "codigoInterno": "ERR_METODO_PAGO_INVALIDO",
                    "mensaje": f"Método de pago '{metodo_pago}' no válido. Métodos permitidos: {', '.join(metodos_validos)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Validar regla de negocio: Cliente existe (si aplica)
        # Agrega aquí validación de cliente si es necesario
        
        # Validar regla de negocio: La venta debe tener al menos un item
        if not items or len(items) == 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Conflict",
                    "codigoInterno": "ERR_VENTA_SIN_ITEMS",
                    "mensaje": "La venta debe incluir al menos un producto.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Crear venta (stock se decrementa automáticamente en la transacción)
        try:
            venta = self.venta_repo.crear_venta_con_items(
                cliente_id=cliente_id,
                items=items,
                metodo_pago=metodo_pago
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Conflict",
                    "codigoInterno": "ERR_VENTA_STOCK_INSUFICIENTE",
                    "mensaje": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Retornar respuesta con formato estandarizado y código HTTP 201
        return {
            "status": "success",
            "mensaje": "Venta registrada exitosamente.",
            "data": {
                "id": venta.id,
                "numero_venta": venta.numero_venta,
                "cliente_id": cliente_id,
                "fecha_venta": venta.fecha_venta.isoformat() if hasattr(venta.fecha_venta, 'isoformat') else venta.fecha_venta,
                "monto_total": float(venta.monto_total),
                "metodo_pago": metodo_pago,
                "estado": venta.estado.value if hasattr(venta.estado, 'value') else venta.estado,
                "items": [
                    {
                        "producto_id": item.get("producto_id"),
                        "cantidad": item.get("cantidad"),
                        "precio_unitario": float(item.get("precio_unitario")) if item.get("precio_unitario") else None,
                        "subtotal": float(item.get("cantidad", 0) * item.get("precio_unitario", 0))
                    }
                    for item in items
                ]
            }
        }