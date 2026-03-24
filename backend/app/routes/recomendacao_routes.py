from fastapi import APIRouter, HTTPException
from app.services.recomendacao_service import criar_recomendacao, buscar_recomendacoes_por_deteccao, gerar_recomendacao_openrouter
from app.shemas.Recomendacao_shema import RecomendacaoRead

router = APIRouter(prefix="/recomendacoes", tags=["recomendacoes"])

@router.get("/{deteccao_id}", response_model=list[RecomendacaoRead], operation_id="listar_recomendacoes_por_deteccao")
def listar_recomendacoes(deteccao_id: int):
    try:
        recomendacoes = buscar_recomendacoes_por_deteccao(deteccao_id)
        return recomendacoes
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{deteccao_id}", response_model=RecomendacaoRead)
def criar_recomendacao_endpoint(deteccao_id: int):
    try:
        deteccao = deteccao_id
        texto = gerar_recomendacao_openrouter(f"Doença detectada: {deteccao.doenca_nome}")
        recomendacao = criar_recomendacao(deteccao_id, texto)
        return recomendacao
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))