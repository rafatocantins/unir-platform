"""Ponto de entrada da API UNIR Platform."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, proposals, events, transparency, public

# Criar tabelas na base de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(auth.router)
app.include_router(proposals.router)
app.include_router(events.router)
app.include_router(transparency.router)
app.include_router(public.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "version": settings.version}
