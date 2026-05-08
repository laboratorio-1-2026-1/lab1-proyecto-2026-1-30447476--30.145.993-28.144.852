from fastapi import APIRouter
from app.api.v1.endpoints import categoriasMaquinas_router, maquinas_router, ticketsMantenimiento_router, productos_router, ventas_router

router = APIRouter()
router.include_router(categoriasMaquinas_router, prefix="/api/v1")
router.include_router(maquinas_router, prefix="/api/v1")
router.include_router(ticketsMantenimiento_router, prefix="/api/v1")
router.include_router(productos_router, prefix="/api/v1")
router.include_router(ventas_router, prefix="/api/v1")