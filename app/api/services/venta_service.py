from app.repositories.venta_repository import VentaRepository
from app.repositories.producto_repository import ProductoRepository
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict

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
                    detail=f"Producto {item['producto_id']} no encontrado"
                )
           
            if producto.stock < item["cantidad"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": "Conflict",
                        "codigoInterno": "ERR_VENTA_STOCK_INSUFICIENTE",
                        "mensaje": f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}, Solicitado: {item['cantidad']}"
                    }
                )
       
        #  Crear venta (stock se decrementa automáticamente en la transacción)
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
                    "mensaje": str(e)
                }
            )
       
        return {
            "id": venta.id,
            "numero_venta": venta.numero_venta,
            "fecha_venta": venta.fecha_venta,
            "monto_total": venta.monto_total,
            "estado": venta.estado.value
        } 
