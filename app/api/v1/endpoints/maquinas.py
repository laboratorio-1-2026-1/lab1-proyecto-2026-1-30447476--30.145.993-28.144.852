from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.db.database import get_db
from app.api.core.security import require_roles
from app.api.core.errors import conflict_response, bad_request_response
from app.api.schemas.schemas import (
    MaquinaCreate,
    MaquinaUpdate,
    MaquinaEstadoUpdate,
    MaquinaOut,
)
from app.api.repositories.maquina_repository import MaquinaRepository

router = APIRouter(prefix="/api/v1", tags=["Máquinas e Instalaciones"])

ESTADOS_VALIDOS = ["Activa", "En Mantenimiento", "Fuera de Servicio"]


@router.get(
    "/maquinas",
    response_model=List[MaquinaOut],
    summary="Listar máquinas (filtros opcionales: categoria_id, estado)",
)
def listar_maquinas(
    categoria_id: Optional[int] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(require_roles("Administrador", "Entrenador")),
):
    if estado and estado not in ESTADOS_VALIDOS:
        return bad_request_response(
            "ERR_ESTADO_INVALIDO",
            f"Estado inválido. Valores permitidos: {ESTADOS_VALIDOS}",
        )
    return MaquinaRepository.get_all(db, categoria_id=categoria_id, estado=estado)


@router.post(
    "/maquinas",
    response_model=MaquinaOut,
    status_code=201,
    summary="Registrar nueva máquina",
)
def crear_maquina(
    data: MaquinaCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("Administrador")),
):
    # Validar categoría
    if not MaquinaRepository.get_categoria_by_id(db, data.categoria_id):
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # Validar número de serie único
    if data.numeroSerie and MaquinaRepository.get_by_numero_serie(db, data.numeroSerie):
        return conflict_response(
            "ERR_SERIE_DUPLICADA",
            f"Ya existe una máquina con el número de serie '{data.numeroSerie}'.",
        )

    return MaquinaRepository.create(db, data)


@router.get(
    "/maquinas/{maquina_id}",
    response_model=MaquinaOut,
    summary="Obtener detalle de una máquina",
)
def obtener_maquina(
    maquina_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles("Administrador", "Entrenador")),
):
    maquina = MaquinaRepository.get_by_id(db, maquina_id)
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    return maquina


@router.put(
    "/maquinas/{maquina_id}",
    response_model=MaquinaOut,
    summary="Actualizar datos de una máquina",
)
def actualizar_maquina(
    maquina_id: int,
    data: MaquinaUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("Administrador")),
):
    # Validar número de serie si se está cambiando
    if data.numeroSerie:
        existente = MaquinaRepository.get_by_numero_serie(db, data.numeroSerie)
        if existente and existente.idMaquinas != maquina_id:
            return conflict_response(
                "ERR_SERIE_DUPLICADA",
                f"Ya existe otra máquina con el número de serie '{data.numeroSerie}'.",
            )

    maquina = MaquinaRepository.update(db, maquina_id, data)
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    return maquina


@router.patch(
    "/maquinas/{maquina_id}/estado",
    response_model=MaquinaOut,
    summary="Cambiar estado operativo de una máquina",
)
def cambiar_estado(
    maquina_id: int,
    data: MaquinaEstadoUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("Administrador")),
):
    if data.estadoOperativo not in ESTADOS_VALIDOS:
        return bad_request_response(
            "ERR_ESTADO_INVALIDO",
            f"Estado inválido. Valores permitidos: {ESTADOS_VALIDOS}",
        )

    maquina = MaquinaRepository.update_estado(db, maquina_id, data.estadoOperativo)
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    return maquina
    