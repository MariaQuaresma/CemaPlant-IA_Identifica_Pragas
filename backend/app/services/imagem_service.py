from app.models.Imagem import Imagem
from app.database import SessionLocal

def criar_imagem(usuario_id: int, url_imagem: str):
    db = SessionLocal()
    nova_imagem = Imagem(usuario_id=usuario_id, url_imagem=url_imagem)
    db.add(nova_imagem)
    db.commit()
    db.refresh(nova_imagem)
    db.close()
    return nova_imagem

def buscar_imagem_por_id(imagem_id: int):
    db = SessionLocal()
    imagem = db.query(Imagem).filter(Imagem.id == imagem_id).first()
    db.close()
    return imagem

def listar_imagens_por_usuario(usuario_id: int):
    db = SessionLocal()
    try:
        imagens = db.query(Imagem).filter(Imagem.usuario_id == usuario_id).all()
        return imagens
    finally:
        db.close()

def listar_todas_imagens():
    db = SessionLocal()
    try:
        return db.query(Imagem).all()
    finally:
        db.close()