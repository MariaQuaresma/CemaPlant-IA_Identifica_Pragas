from app.models.Recomendacao import Recomendacao
from app.models.Deteccao import Deteccao
from app.models.Doenca import Doenca
from app.database import SessionLocal
from fastapi import HTTPException
import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def gerar_recomendacao_openrouter(doenca_nome: str) -> str:
    prompt = f"""
    A planta apresenta a doença: {doenca_nome}.
    Gere uma recomendação simples, natural e prática para tratar essa doença.
    Evite produtos químicos fortes.
    """
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    data = response.json()
    if "choices" not in data:
        raise Exception(f"Erro OpenRouter: {data}")
    return data["choices"][0]["message"]["content"]

def gerar_recomendacao_por_deteccao(deteccao_id: int) -> str:
    db = SessionLocal()
    try:
        deteccao = db.query(Deteccao).filter(Deteccao.id == deteccao_id).first()
        if not deteccao:
            raise HTTPException(status_code=404, detail="Detecção não encontrada")
        doenca = db.query(Doenca).filter(Doenca.id == deteccao.doenca_id).first()
        nome_doenca = doenca.nome if doenca else "desconhecida"
        return gerar_recomendacao_openrouter(nome_doenca)
    finally:
        db.close()

def criar_recomendacao(deteccao_id: int, texto: str):
    db = SessionLocal()
    try:
        deteccao = db.query(Deteccao).filter(Deteccao.id == deteccao_id).first()
        if not deteccao:
            raise HTTPException(status_code=404, detail="Detecção não encontrada")
        recomendacao = Recomendacao(
            deteccao_id=deteccao_id,
            texto_recomendacao=texto
        )
        db.add(recomendacao)
        db.commit()
        db.refresh(recomendacao)
        return recomendacao
    finally:
        db.close()

def buscar_recomendacoes_por_deteccao(deteccao_id: int):
    db = SessionLocal()
    try:
        return db.query(Recomendacao).filter(
            Recomendacao.deteccao_id == deteccao_id
        ).all()
    finally:
        db.close()