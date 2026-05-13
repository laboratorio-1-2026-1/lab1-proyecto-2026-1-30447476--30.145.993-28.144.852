from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.api.database.session import Base

class Producto(Base):
    __tablename__ = "productosTienda"   # nombre exacto según MER

    idProductosTienda = Column(Integer, primary_key=True, index=True)  # idProductosTienda
    nombre = Column(String(100), nullable=False, index=True)
    descripcion = Column(String(500), nullable=True)    # text
    categoria_producto_id = Column(Integer, ForeignKey("categorias_producto.id"), nullable=False)
    precio = Column(Float, nullable=False)              # decimal(10,2) se puede usar Float
    stock = Column(Integer, default=0, nullable=False)
    codigo_barra = Column(String(50), unique=True, nullable=True)  # opcional, pero único
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación (opcional)
    categoria = relationship("CategoriaProducto", backref="productos")
    detalles = relationship("VentaDetalle", back_populates="producto")
