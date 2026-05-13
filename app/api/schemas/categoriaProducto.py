from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class CategoriaProductoBase(BaseModel):
    nombre: str = Field(..., max_length=50, description="Nombre de la categoría de producto")
    descripcion: Optional[str] = Field(None, description="Descripción de la categoría")

class CategoriaProductoCreate(BaseModel):
    nombre: str = Field(..., max_length=50)
    descripcion: Optional[str] = None

class CategoriaProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = None

class CategoriaProductoResponse(CategoriaProductoBase):
    idCategoriasProductos: int = Field(..., description="ID único de la categoría")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)