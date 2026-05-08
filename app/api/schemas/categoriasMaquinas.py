from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class CategoriaMaquinaBase(BaseModel):
    nombre: str = Field(..., max_length=50, description="Nombre de la categoría (ej. Cardio, Pesas)")
    descripcion: Optional[str] = Field(None, description="Descripción detallada de la categoría")

class CategoriaMaquinaCreate(BaseModel):
    nombre: str = Field(..., max_length=50, description="Nombre de la categoría")
    descripcion: Optional[str] = Field(None, description="Descripción detallada")

class CategoriaMaquinaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=50, description="Nombre de la categoría")
    descripcion: Optional[str] = Field(None, description="Descripción detallada")

class CategoriaMaquinaResponse(BaseModel):
    idCategoriasMaquinas: int = Field(..., description="ID único de la categoría")
    nombre: str = Field(..., max_length=50, description="Nombre de la categoría")
    descripcion: Optional[str] = Field(None, description="Descripción detallada")
    created_at: datetime = Field(..., description="Fecha y hora de creación")

    model_config = ConfigDict(from_attributes=True)