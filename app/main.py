from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.core.config import settings
from app.api.database.session import engine, Base
from app.api.v1.routers import router as api_router


# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SmartGym API — Laboratorio I 2026-1",
    docs_url="/docs",
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers 
app.include_router(api_router, prefix=settings.API_V1_STR)


# S@app.on_event("startup")
# async def startup():
#    create_tables()
#    print(f"✅ {settings.PROJECT_NAME} iniciado")
#    print("📚 Docs: http://localhost:8000/docs")


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "docs": "/docs"}