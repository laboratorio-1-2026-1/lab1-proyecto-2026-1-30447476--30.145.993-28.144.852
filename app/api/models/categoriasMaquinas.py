from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base  

class CategoriaMaquina(Base):
    __tablename__ = "categorias_maquinas"

    idCategoriasMaquinas = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relación 
    maquinas = relationship("Maquina", back_populates="categoria")