from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from app.routes import usuario_routes
from app.routes import planta_routes
from app.routes import deteccao_routes
from app.routes import recomendacao_routes
from app.routes import doenca_routes
from app.routes import imagem_routes

def _load_cors_origins() -> list[str]:
    default_origins = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "null",
    ]
    env_origins = os.getenv("CORS_ALLOW_ORIGINS", "")
    if not env_origins.strip():
        return default_origins
    return [origin.strip() for origin in env_origins.split(",") if origin.strip()]

app = FastAPI(
    title="CemaPlant API",
    description="API para identificação de doenças com IA",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"

app.add_middleware(
    CORSMiddleware,
    allow_origins=_load_cors_origins(),
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuario_routes.router)
app.include_router(deteccao_routes.router)
app.include_router(planta_routes.router)
app.include_router(doenca_routes.router)
app.include_router(recomendacao_routes.router)
app.include_router(imagem_routes.router)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

@app.get("/")
def home():
    return {
        "status": "CemaPlant API funcionando",
        "versao": "1.0.0",
        "descricao": "API para identificação de pragas em plantas com IA"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}