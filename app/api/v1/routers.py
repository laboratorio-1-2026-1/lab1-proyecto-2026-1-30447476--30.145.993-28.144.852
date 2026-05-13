from fastapi import APIRouter
from app.api.v1.endpoints.maquinas import router as maquinas_router
from app.api.v1.endpoints.categoriasMaquinas import router as categoriasMaquinas_router
from app.api.v1.endpoints.mantenimiento import router as ticketsMantenimiento_router
from app.api.v1.endpoints.productos import router as productos_router
from app.api.v1.endpoints.ventas import router as ventas_router

router = APIRouter()
router.include_router(categoriasMaquinas_router, prefix="/api/v1", tags=["Categorías"])
router.include_router(maquinas_router, prefix="/api/v1", tags=["Máquinas"])
router.include_router(ticketsMantenimiento_router, prefix="/api/v1", tags=["Mantenimiento"])
router.include_router(productos_router, prefix="/api/v1", tags=["Productos"])
router.include_router(ventas_router, prefix="/api/v1", tags=["Ventas"])