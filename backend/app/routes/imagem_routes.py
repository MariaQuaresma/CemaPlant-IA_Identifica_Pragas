from fastapi import APIRouter, HTTPException
from app.services.imagem_service import buscar_imagem_por_id, listar_imagens_por_usuario
from app.schemas.Imagem_schema import ImagemRead

router = APIRouter(prefix="/imagens", tags=["imagens"])

@router.get("/{imagem_id}", response_model=ImagemRead)
def buscar_imagem(imagem_id: int):
    imagem = buscar_imagem_por_id(imagem_id)
    if not imagem:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    return imagem

@router.get("/usuario/{usuario_id}", response_model=list[ImagemRead])
def listar_imagens_usuario(usuario_id: int):
    try:
        return listar_imagens_por_usuario(usuario_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))