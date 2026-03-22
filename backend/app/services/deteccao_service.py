from app.models.Deteccao import Deteccao
from app.database import SessionLocal
from app.IA.predict import prever_doenca

def salvar_deteccao(imagem_id: int, planta_id: int, doenca_id: int, porcentagem_confianca: float):
    db = SessionLocal()
    try:
        nova_deteccao = Deteccao(
            imagem_id=imagem_id,
            planta_id=planta_id,
            doenca_id=doenca_id,
            porcentagem_confianca=porcentagem_confianca
        )
        db.add(nova_deteccao)
        db.commit()
        db.refresh(nova_deteccao)
        return nova_deteccao
    finally:
        db.close()

def buscar_deteccao_por_id(deteccao_id: int):
    db = SessionLocal()
    try:
        return db.query(Deteccao).filter(Deteccao.id == deteccao_id).first()
    finally:
        db.close()

def detectar_doenca(caminho_imagem: str):
    resultado = prever_doenca(caminho_imagem)
    return {
        "doenca_nome": resultado["classe_nome"],
        "confianca": resultado["confianca"]
    }
