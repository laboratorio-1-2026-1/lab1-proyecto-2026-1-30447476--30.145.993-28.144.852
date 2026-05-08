from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class ItemVenta(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0)
    precio_unitario: float = Field(..., gt=0)

class VentaCreate(BaseModel):
    cliente_id: Optional[int] = None
    items: List[ItemVenta]
    metodo_pago: str

class VentaResponse(BaseModel):
    id: int
    numero_venta: str
    fecha_venta: datetime
    monto_total: float
    estado: str
    
    class Config:
        from_attributes = True