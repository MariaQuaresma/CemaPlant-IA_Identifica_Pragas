from fastapi import APIRouter
from app.database import SessionLocal
from app.models.Doenca import Doenca
from app.schemas.Doenca_schema import DoencaRead
from fastapi import APIRouter, HTTPException, Depends
from app.database import SessionLocal
from app.models.Doenca import Doenca
from app.schemas.Doenca_schema import DoencaRead
from app.auth.authentication import get_usuario_logado
from app.services.doenca_service import (listar_doencas_por_usuario, buscar_doenca_por_id)

router = APIRouter(prefix="/doencas", tags=["doencas"])
@router.get("/usuario", response_model=list[DoencaRead])

def listar_doencas_usuario(usuario=Depends(get_usuario_logado)):
    try:
        return listar_doencas_por_usuario(usuario.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/todas", response_model=list[DoencaRead])
def listar_doencas(usuario=Depends(get_usuario_logado)):
    db = SessionLocal()
    try:
        return db.query(Doenca).all()
    finally:
        db.close()

@router.get("/{doenca_id}", response_model=DoencaRead)
def buscar_doenca(doenca_id: int, usuario=Depends(get_usuario_logado)):
    try:
        return buscar_doenca_por_id(doenca_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))