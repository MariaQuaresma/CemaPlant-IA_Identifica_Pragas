from fastapi import APIRouter, HTTPException
from app.services.usuario_service import criar_usuario, autenticar_usuario
from app.schemas.Usuario_shema import UsuarioCreate, UsuarioRead

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("/registrar", response_model=UsuarioRead)
def register_usuario(usuario: UsuarioCreate):
    try:
        novo_usuario = criar_usuario(usuario.nome, usuario.email, usuario.senha)
        return novo_usuario
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=UsuarioRead)
def login_usuario(usuario: UsuarioCreate):
    usuario_autenticado = autenticar_usuario(usuario.email, usuario.senha)
    if not usuario_autenticado:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return usuario_autenticado
