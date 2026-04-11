from fastapi import Request, HTTPException, Depends
from app.models.Usuario import Usuario
from app.database import SessionLocal
from app.auth.security import verificar_token  

def get_usuario_logado(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Não autenticado (cookie não enviado)"
        )
    payload = verificar_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado"
        )
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Token inválido (sem user_id)"
        )
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not usuario:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado"
            )
        return usuario
    finally:
        db.close()