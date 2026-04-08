from fastapi import APIRouter, HTTPException
from app.services.recomendacao_service import (
    criar_recomendacao,
    buscar_recomendacoes_por_deteccao,
    gerar_recomendacao_por_deteccao
)
from app.schemas.Recomendacao_schema import RecomendacaoRead

router = APIRouter(prefix="/recomendacoes", tags=["recomendacoes"])

@router.post("/{deteccao_id}", response_model=RecomendacaoRead)
def gerar_recomendacao(deteccao_id: int):
    try:
        texto = gerar_recomendacao_por_deteccao(deteccao_id)
        return criar_recomendacao(deteccao_id, texto)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{deteccao_id}", response_model=list[RecomendacaoRead])
def listar_recomendacoes(deteccao_id: int):
    return buscar_recomendacoes_por_deteccao(deteccao_id)