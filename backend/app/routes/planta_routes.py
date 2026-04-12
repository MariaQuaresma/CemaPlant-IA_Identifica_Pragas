from fastapi import APIRouter, HTTPException, Depends
from app.database import SessionLocal
from app.models.Planta import Planta
from app.schemas.Planta_schema import PlantaRead
from app.services.planta_service import criar_planta, listar_plantas, buscar_planta_por_id, atualizar_planta, deletar_planta, listar_plantas_por_usuario
from app.auth.authentication import get_usuario_logado

router = APIRouter(prefix="/plantas", tags=["plantas"])
@router.get("/usuario", response_model=list[PlantaRead])
def listar_plantas_usuario(usuario=Depends(get_usuario_logado)):
    try:
        plantas = listar_plantas_por_usuario(usuario.id)
        return plantas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/todas", response_model=list[PlantaRead])
def listar_plantas(usuario=Depends(get_usuario_logado)):
    db = SessionLocal()
    try:
        return db.query(Planta).all()
    finally:
        db.close()

@router.get("/{planta_id}", response_model=PlantaRead)
def buscar_planta(planta_id: int, usuario=Depends(get_usuario_logado)):
    db = SessionLocal()
    try:
        planta = db.query(Planta).filter(Planta.id == planta_id).first()
        if not planta:
            raise HTTPException(status_code=404, detail="Planta não encontrada")
        return planta
    finally:
        db.close()