from app.models.Recomendacao import Recomendacao
from app.models.Deteccao import Deteccao
from app.models.Doenca import Doenca
from app.models.Planta import Planta
from app.database import SessionLocal
from fastapi import HTTPException
import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def gerar_recomendacao_openrouter(doenca_nome: str, planta_nome: str) -> str:
    nome_limpo = doenca_nome.split("___")[-1].replace("_", " ")
    prompt = f"""
    A planta é: {planta_nome}
    A doença detectada é: {nome_limpo}
    Gere uma recomendação:
    - prática e natural
    - específica para essa planta
    - simples para leigos
    - sem produtos químicos fortes
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
        recomendacao_existente = db.query(Recomendacao).filter(
            Recomendacao.deteccao_id == deteccao_id
        ).first()
        if recomendacao_existente:
            return recomendacao_existente.texto_recomendacao
        deteccao = db.query(Deteccao).filter(Deteccao.id == deteccao_id).first()
        if not deteccao:
            raise HTTPException(status_code=404, detail="Detecção não encontrada")
        doenca = db.query(Doenca).filter(Doenca.id == deteccao.doenca_id).first()
        planta = db.query(Planta).filter(Planta.id == deteccao.planta_id).first()
        nome_doenca = doenca.nome if doenca else ""
        nome_planta = planta.nome if planta else "planta"
        if "healthy" in nome_doenca.lower() or nome_doenca.strip() == "":
            return f"A planta {nome_planta} está saudável 🌱. Nenhum tratamento é necessário. Apenas mantenha rega adequada, luz solar e boa ventilação."
        return gerar_recomendacao_openrouter(nome_doenca, nome_planta)
    finally:
        db.close()

def criar_recomendacao(deteccao_id: int, texto: str):
    db = SessionLocal()
    try:
        existente = db.query(Recomendacao).filter(
            Recomendacao.deteccao_id == deteccao_id
        ).first()
        if existente:
            return existente
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