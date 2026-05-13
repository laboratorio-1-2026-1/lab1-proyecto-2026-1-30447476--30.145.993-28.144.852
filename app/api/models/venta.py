from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
import enum
from app.api.models.base import Base, TimestampMixin

class EstadoVenta(str, enum.Enum):
    COMPLETADA = "COMPLETADA"
    DEVUELTA = "DEVUELTA"
    CANCELADA = "CANCELADA"

# Tabla asociativa para items de venta
venta_producto_association = Table(
    'venta_productos',
    Base.metadata,
    Column('venta_id', Integer, ForeignKey('ventas.id')),
    Column('producto_id', Integer, ForeignKey('productos.id')),
    Column('cantidad', Integer),
    Column('precio_unitario', Float)
)

class Venta(Base, TimestampMixin):
    __tablename__ = "ventas"
   
    idVenta = Column(Integer, primary_key=True, index=True)
    numero_venta = Column(String(50), unique=True, nullable=False)
    fecha_venta = Column(DateTime, nullable=False)
    monto_total = Column(Float, nullable=False)
    metodo_pago = Column(String(50))
    estado = Column(Enum(EstadoVenta), default=EstadoVenta.COMPLETADA)
   
    # Relación con cliente
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    cliente = relationship("Cliente", back_populates="ventas") 

    # Relación con los detalles de venta
    detalles = relationship(
        "VentaDetalle", 
        back_populates="venta", 
        cascade="all, delete-orphan"
    )