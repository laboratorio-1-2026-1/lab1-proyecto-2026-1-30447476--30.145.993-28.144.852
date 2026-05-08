from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TicketCreate(BaseModel):
    maquina_id: int
    descripcion: str = Field(..., min_length=10, max_length=500)
    urgencia: str  # CRITICA, ALTA, MEDIA, BAJA
    observaciones: Optional[str] = None

class TicketUpdate(BaseModel):
    estado: str  # ABIERTO, EN_REPARACION, REPARADO, CERRADO
    costo_reparacion: Optional[float] = None

class TicketResponse(BaseModel):
    id: int
    maquina_id: int
    descripcion: str
    urgencia: str
    estado: str
    fecha_creacion: datetime
   
    class Config:
        from_attributes = True