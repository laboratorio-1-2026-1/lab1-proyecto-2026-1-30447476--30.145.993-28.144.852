from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.models import VentaTienda, VentaDetalle, ProductoTienda


class VentaRepository:

    @staticmethod
    def get_all(db: Session) -> List[VentaTienda]:
        return db.query(VentaTienda).order_by(VentaTienda.fechaVenta.desc()).all()

    @staticmethod
    def get_by_id(db: Session, venta_id: int) -> Optional[VentaTienda]:
        return db.query(VentaTienda).filter(
            VentaTienda.idVentasTiendas == venta_id
        ).first()

    @staticmethod
    def get_by_cliente(db: Session, cliente_id: int) -> List[VentaTienda]:
        return db.query(VentaTienda).filter(
            VentaTienda.cliente_id == cliente_id
        ).order_by(VentaTienda.fechaVenta.desc()).all()

    @staticmethod
    def create(
        db: Session,
        usuario_id: int,
        items: List[dict],          # [{"producto_id": int, "cantidad": int}]
        cliente_id: Optional[int] = None,
        metodo_pago: Optional[str] = None,
    ) -> VentaTienda:
        """
        Crea la venta y sus detalles en una sola transacción.
        Asume que el stock ya fue validado antes de llamar este método.
        """
        total = Decimal("0.00")
        detalles_data = []

        for item in items:
            producto = db.query(ProductoTienda).filter(
                ProductoTienda.idProductosTienda == item["producto_id"]
            ).first()

            precio_unitario = producto.precio
            subtotal = precio_unitario * item["cantidad"]
            total += subtotal

            # Descontar stock dentro de la misma transacción
            producto.stock -= item["cantidad"]

            detalles_data.append({
                "producto_id": item["producto_id"],
                "cantidad": item["cantidad"],
                "precioUnitario": precio_unitario,
                "subtotal": subtotal,
            })

        venta = VentaTienda(
            cliente_id=cliente_id,
            usuario_id=usuario_id,
            total=total,
            metodoPago=metodo_pago,
        )
        db.add(venta)
        db.flush()  # obtener el ID antes de crear detalles

        for d in detalles_data:
            detalle = VentaDetalle(
                venta_id=venta.idVentasTiendas,
                producto_id=d["producto_id"],
                cantidad=d["cantidad"],
                precioUnitario=d["precioUnitario"],
                subtotal=d["subtotal"],
            )
            db.add(detalle)

        db.commit()
        db.refresh(venta)
        return venta

    @staticmethod
    def get_detalles(db: Session, venta_id: int) -> List[VentaDetalle]:
        return db.query(VentaDetalle).filter(
            VentaDetalle.venta_id == venta_id
        ).all() 
