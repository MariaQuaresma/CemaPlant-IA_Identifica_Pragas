from fastapi import APIRouter
from app.database import SessionLocal
from app.models.Doenca import Doenca
from app.schemas.Doenca_schema import DoencaRead

router = APIRouter(prefix="/doencas", tags=["doencas"])

@router.get("/", response_model=list[DoencaRead])
def listar_doencas():
    db = SessionLocal()
    try:
        return db.query(Doenca).all()
    finally:
        db.close()