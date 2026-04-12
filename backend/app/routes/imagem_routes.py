from fastapi import APIRouter, HTTPException, Depends
from app.services.imagem_service import buscar_imagem_por_id, listar_imagens_por_usuario, listar_todas_imagens
from app.schemas.Imagem_schema import ImagemRead
from app.auth.authentication import get_usuario_logado
from app.database import SessionLocal
router = APIRouter(prefix="/imagens", tags=["imagens"])

@router.get("/usuario", response_model=list[ImagemRead])
def listar_imagens_usuario(usuario=Depends(get_usuario_logado)):
    try:
        return listar_imagens_por_usuario(usuario.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=list[ImagemRead])
def listar_todas(usuario=Depends(get_usuario_logado)):
    try:
        return listar_todas_imagens()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{imagem_id}", response_model=ImagemRead)
def buscar_imagem(imagem_id: int, usuario=Depends(get_usuario_logado)):
    imagem = buscar_imagem_por_id(imagem_id)
    if not imagem:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    return imagem