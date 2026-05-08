from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base, TimestampMixin

class EstadoMaquina(str, enum.Enum):
    ACTIVA = "ACTIVA"
    EN_MANTENIMIENTO = "EN MANTENIMIENTO"
    FUERA_DE_SERVICIO = "FUERA DE SERVICIO"

class CategoriaMaquina(Base, TimestampMixin):
    __tablename__ = "categorias_maquinas"
    
    idCategoriasMaquinas = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Relación
    maquinas = relationship("Maquina", back_populates="categoria")

class Maquina(Base, TimestampMixin):
    __tablename__ = "maquinas"
    
    idMaquinas = Column(Integer, primary_key=True, autoincrement=True)
    nombreMaquina = Column(String(100), nullable=False)
    descripcionTecnica = Column(Text, nullable=True)
    estadoOperativo = Column(Enum(EstadoMaquina), default=EstadoMaquina.ACTIVA)
    categoria_id = Column(Integer, ForeignKey("categorias_maquinas.idCategoriasMaquinas"))
    fechaAdquisicion = Column(Date, nullable=True)
    numeroSerie = Column(String(100), unique=True, nullable=True)
    ultimoMantenimiento = Column(Date, nullable=True)
    
    # Relación
    categoria = relationship("CategoriaMaquina", back_populates="maquinas")
    tickets = relationship("TicketMantenimiento", back_populates="maquina")
    
    def __repr__(self):
        return f"<Maquina {self.nombreMaquina} - {self.estadoOperativo}>"
