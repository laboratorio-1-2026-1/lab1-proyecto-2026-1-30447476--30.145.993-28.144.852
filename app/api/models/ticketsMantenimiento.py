from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.api.models.base import Base, TimestampMixin

class TicketMantenimiento(Base, TimestampMixin):
    __tablename__ = "tickets_mantenimiento"
    
    idTicketsMantenimiento = Column(Integer, primary_key=True, autoincrement=True)
    maquina_id = Column(Integer, ForeignKey("maquinas.idMaquinas"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.idUsuarios"), nullable=True)
    fechaReporte = Column(DateTime, nullable=False)
    descripcionFalla = Column(Text, nullable=False)
    fechaResolucion = Column(DateTime, nullable=True)
    costoReparacion = Column(Numeric(10, 2), nullable=True)
    tecnicoResponsable = Column(String(100), nullable=True)
    estado = Column(String(50), default="ABIERTO")
    
    # Relaciones
    maquina = relationship("Maquina", back_populates="tickets")
    
    def __repr__(self):
        return f"<TicketMantenimiento {self.idTicketsMantenimiento} - {self.estado}>"