from fastapi import APIRouter, HTTPException, Depends
from app.services.recomendacao_service import (criar_recomendacao,listar_recomendacoes,listar_recomendacoes_por_usuario, buscar_recomendacao_por_id)
from app.schemas.Recomendacao_schema import RecomendacaoRead
from app.auth.authentication import get_usuario_logado

router = APIRouter(prefix="/recomendacoes", tags=["recomendacoes"])

@router.get("/usuario", response_model=list[RecomendacaoRead])
def listar_recomendacoes_usuario(usuario=Depends(get_usuario_logado)):
    return listar_recomendacoes_por_usuario(usuario.id)

@router.get("/todas", response_model=list[RecomendacaoRead])
def listar_todas_recomendacoes(usuario=Depends(get_usuario_logado)):
    return listar_recomendacoes()

@router.get("/{recomendacao_id}", response_model=RecomendacaoRead)
def buscar_recomendacao(recomendacao_id: int, usuario=Depends(get_usuario_logado)):
    return buscar_recomendacao_por_id(recomendacao_id)