from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import usuario_routes
from app.routes import planta_routes
from app.routes import deteccao_routes
from app.routes import recomendacao_routes
from app.routes import doenca_routes
from app.routes import imagem_routes

app = FastAPI(
    title="CemaPlant API",
    description="API para identificação de doenças com IA",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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