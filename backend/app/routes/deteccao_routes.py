from app.services.deteccao_service import detectar_doenca
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.doenca_service import predizer_doenca
from app.services.imagem_service import criar_imagem
from app.services.deteccao_service import salvar_deteccao
from app.schemas.Deteccao_shema import DeteccaoRead
from app.database import SessionLocal
from app.models.Doenca import Doenca
import os
from app.services.deteccao_service import detectar_doenca as detectar_service

router = APIRouter(prefix="/deteccoes", tags=["deteccoes"])
UPLOAD_DIR = "app/uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=DeteccaoRead)
def detectar_doenca(usuario_id: int, planta_id: int, file: UploadFile = File(...)):
    try:
        caminho = os.path.join(UPLOAD_DIR, file.filename)
        with open(caminho, "wb") as f:
            f.write(file.file.read())
        imagem = criar_imagem(usuario_id, caminho)
        classe_nome, confianca = predizer_doenca(caminho)
        db = SessionLocal()
        try:
            doenca = db.query(Doenca).filter(Doenca.nome == classe_nome).first()
            if not doenca:
                raise HTTPException(status_code=404, detail="Doença não cadastrada no banco")
            doenca_id = doenca.id
            deteccao = salvar_deteccao(imagem.id, planta_id, doenca_id, confianca)
            return deteccao
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar imagem: {str(e)}")

@router.post("/detectar")
def detectar(file: UploadFile):
    caminho = os.path.join(UPLOAD_DIR, file.filename)
    with open(caminho, "wb") as f:
        f.write(file.file.read())
    resultado = detectar_service(caminho)
    return resultado