from fastapi import APIRouter, HTTPException
from app.services.recomendacao_service import (criar_recomendacao,buscar_recomendacoes_por_deteccao,gerar_recomendacao_por_deteccao)
from app.schemas.Recomendacao_shema import RecomendacaoRead

router = APIRouter(prefix="/deteccoes", tags=["recomendacoes"])

@router.post("/{deteccao_id}/recomendacao", response_model=RecomendacaoRead)
def gerar_recomendacao(deteccao_id: int):
    try:
        texto = gerar_recomendacao_por_deteccao(deteccao_id)
        recomendacao = criar_recomendacao(deteccao_id, texto)
        return recomendacao
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{deteccao_id}/recomendacoes", response_model=list[RecomendacaoRead])
def listar_recomendacoes(deteccao_id: int):
    return buscar_recomendacoes_por_deteccao(deteccao_id)