from fastapi import APIRouter, HTTPException
from app.services.imagem_service import buscar_imagem_por_id
from app.database import SessionLocal
from app.models.Planta import Planta
from app.schemas.Planta_shema import PlantaRead

router = APIRouter(prefix="/plantas", tags=["plantas"])

@router.get("/", response_model=list[PlantaRead])
def listar_plantas():
    db = SessionLocal()
    try:
        plantas = db.query(Planta).all()
        return plantas
    finally:
        db.close()

@router.get("/{planta_id}", response_model=PlantaRead)
def buscar_planta(planta_id: int):
    db = SessionLocal()
    try:
        planta = db.query(Planta).filter(Planta.id == planta_id).first()
        if not planta:
            raise HTTPException(status_code=404, detail="Planta não encontrada")
        return planta
    finally:
        db.close()
