from app.database import SessionLocal
from app.models.Usuario import Usuario
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def criar_usuario(nome: str, email: str, senha: str) -> Usuario:
    db = SessionLocal()
    try:
        senha_hash = pwd_context.hash(senha)
        usuario = Usuario(
            nome=nome,
            email=email,
            senha=senha_hash
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario
    except IntegrityError:
        db.rollback()
        raise ValueError("Email já cadastrado")
    finally:
        db.close()

def autenticar_usuario(email: str, senha: str) -> Usuario | None:
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if usuario and pwd_context.verify(senha, usuario.senha):
            return usuario
        return None
    finally:
        db.close()