from fastapi import FastAPI
from app.database.session import engine, Base
from app.api.v1.routers import router as api_router
from app.core.dependencies import get_current_user  # si lo necesita
from app.routers import categoriasMaquinas, maquinas, ticketsMantenimiento
from app.routers import productos, ventas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartGym API", version="1.0.0")
app.include_router(api_router)
app.include_router(categoriasMaquinas.router)
app.include_router(maquinas.router)
app.include_router(ticketsMantenimiento.router)
app.include_router(productos.router)
app.include_router(ventas.router)