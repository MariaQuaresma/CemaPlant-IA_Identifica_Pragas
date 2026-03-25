from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from app.models.Doenca import Doenca
from app.schemas.Doenca_shema import DoencaRead
router = APIRouter(prefix="/doencas", tags=["doencas"])

@router.get("/", response_model=list[DoencaRead])
def listar_doencas():
    db = SessionLocal()
    try:
        doencas = db.query(Doenca).all()
        return doencas
    finally:
        db.close()

@router.get("/{doenca_id}", response_model=DoencaRead)
def buscar_doenca(doenca_id: int):
    db = SessionLocal()
    try:
        doenca = db.query(Doenca).filter(Doenca.id == doenca_id).first()
        if not doenca:
            raise HTTPException(status_code=404, detail="Doença não encontrada")
        return doenca
    finally:
        db.close()