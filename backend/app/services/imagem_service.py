from app.models.Imagem import Imagem
from app.database import SessionLocal
from datetime import timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    TZ_BRASILIA = ZoneInfo("America/Sao_Paulo")
except ZoneInfoNotFoundError:
    TZ_BRASILIA = timezone.utc

def _normalizar_data_upload(imagem: Imagem):
    if not imagem or not imagem.data_upload:
        return imagem
    data = imagem.data_upload
    if data.tzinfo is None:
        data = data.replace(tzinfo=timezone.utc)
    imagem.data_upload = data.astimezone(TZ_BRASILIA)
    return imagem

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
    return _normalizar_data_upload(imagem)

def listar_imagens_por_usuario(usuario_id: int):
    db = SessionLocal()
    try:
        imagens = db.query(Imagem).filter(Imagem.usuario_id == usuario_id).all()
        for imagem in imagens:
            _normalizar_data_upload(imagem)
        return imagens
    finally:
        db.close()

def listar_todas_imagens():
    db = SessionLocal()
    try:
        imagens = db.query(Imagem).all()
        for imagem in imagens:
            _normalizar_data_upload(imagem)
        return imagens
    finally:
        db.close()