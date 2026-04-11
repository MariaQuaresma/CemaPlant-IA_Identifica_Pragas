import numpy as np
from PIL import Image
import os
from app.IA.predict import prever_doenca
from app.database import SessionLocal
from app.models.Doenca import Doenca
from app.models.Deteccao import Deteccao
from app.models.Imagem import Imagem
from fastapi import HTTPException

def predizer_doenca(caminho_imagem: str) -> tuple[str, float]:
    try:
        if not os.path.exists(caminho_imagem):
            raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}") 
        resultado = prever_doenca(caminho_imagem)
        img = Image.open(caminho_imagem).convert("RGB")
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        print(f"[IA] Imagem processada: {img_array.shape}")
        classe_nome, confianca = resultado
        print(f"[IA] Doença detectada: {classe_nome} ({confianca * 100:.2f}%)")
        return classe_nome, float(confianca)
    except Image.UnidentifiedImageError:
        raise ValueError(f"Arquivo não é uma imagem válida: {caminho_imagem}")
    except Exception as e:
        raise Exception(f"Erro ao processar imagem: {str(e)}")
    
def listar_doencas_por_usuario(usuario_id: int):
    db = SessionLocal()
    try:
        doencas = (
            db.query(Doenca)
            .join(Deteccao, Deteccao.doenca_id == Doenca.id)
            .join(Imagem, Deteccao.imagem_id == Imagem.id)
            .filter(Imagem.usuario_id == usuario_id)
            .distinct()
            .all()
        )
        return doencas
    finally:
        db.close()

def buscar_doenca_por_id(doenca_id: int):
    db = SessionLocal()
    try:
        doenca = db.query(Doenca).filter(Doenca.id == doenca_id).first()
        if not doenca:
            raise HTTPException(status_code=404, detail="Doença não encontrada")
        return doenca
    finally:
        db.close()