from fastapi import APIRouter, HTTPException, Response
from app.services.usuario_service import criar_usuario, autenticar_usuario
from app.schemas.Usuario_schema import UsuarioCreate, UsuarioLogin, UsuarioRead
from app.auth.security import criar_token

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("/registrar", response_model=UsuarioRead)
def register_usuario(usuario: UsuarioCreate):
    try:
        return criar_usuario(usuario.nome, usuario.email, usuario.senha)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login_usuario(usuario: UsuarioLogin, response: Response):
    usuario_autenticado = autenticar_usuario(usuario.email, usuario.senha)
    if not usuario_autenticado:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = criar_token({"user_id": usuario_autenticado.id})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False  
    )
    return {"message": "Login realizado com sucesso"}