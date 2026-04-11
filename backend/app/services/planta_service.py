from app.database import SessionLocal
from app.models.Planta import Planta
from fastapi import HTTPException
from app.database import SessionLocal
from app.models.Planta import Planta
from app.models.Deteccao import Deteccao
from app.models.Imagem import Imagem

def criar_planta(nome: str, nome_cientifico: str, descricao: str):
    db = SessionLocal()
    try:
        planta = Planta(nome=nome, nome_cientifico=nome_cientifico,descricao=descricao)
        db.add(planta)
        db.commit()
        db.refresh(planta)
        return planta
    finally:
        db.close()


def listar_plantas():
    db = SessionLocal()
    try:
        return db.query(Planta).all()
    finally:
        db.close()


def buscar_planta_por_id(planta_id: int):
    db = SessionLocal()
    try:
        planta = db.query(Planta).filter(Planta.id == planta_id).first()
        if not planta:
            raise HTTPException(status_code=404, detail="Planta não encontrada")
        return planta
    finally:
        db.close()


def atualizar_planta(planta_id: int, nome: str, nome_cientifico: str, descricao: str):
    db = SessionLocal()
    try:
        planta = db.query(Planta).filter(Planta.id == planta_id).first()
        if not planta:
            raise HTTPException(status_code=404, detail="Planta não encontrada")
        planta.nome = nome
        planta.nome_cientifico = nome_cientifico
        planta.descricao = descricao
        db.commit()
        db.refresh(planta)
        return planta
    finally:
        db.close()


def deletar_planta(planta_id: int):
    db = SessionLocal()
    try:
        planta = db.query(Planta).filter(Planta.id == planta_id).first()
        if not planta:
            raise HTTPException(status_code=404, detail="Planta não encontrada")
        db.delete(planta)
        db.commit()
        return {"message": "Planta deletada com sucesso"}
    finally:
        db.close()

def listar_plantas_por_usuario(usuario_id: int):
    db = SessionLocal()
    try:
        plantas = (
            db.query(Planta)
            .join(Deteccao, Deteccao.planta_id == Planta.id)
            .join(Imagem, Deteccao.imagem_id == Imagem.id)
            .filter(Imagem.usuario_id == usuario_id)
            .distinct()
            .all()
        )
        return plantas
    finally:
        db.close()