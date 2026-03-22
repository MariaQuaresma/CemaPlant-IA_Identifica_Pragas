from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.doenca_service import predizer_doenca
from app.services.imagem_service import criar_imagem
from app.services.deteccao_service import salvar_deteccao
from app.shemas.Deteccao_shema import DeteccaoRead
import os
from app.services.deteccao_service import detectar_doenca

router = APIRouter(prefix="/deteccoes", tags=["deteccoes"])

UPLOAD_DIR = "backend/app/uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=DeteccaoRead)
def detectar_praga(usuario_id: int, planta_id: int, file: UploadFile = File(...)):
    try:
        caminho = os.path.join(UPLOAD_DIR, file.filename)
        with open(caminho, "wb") as f:f.write(file.file.read())
        imagem = criar_imagem(usuario_id, caminho)
        doenca_id, confianca = predizer_doenca(caminho)
        deteccao = salvar_deteccao(imagem.id, planta_id, doenca_id, confianca)
        return deteccao
    except Exception as e: raise HTTPException(status_code=400, detail=f"Erro ao processar imagem: {str(e)}")

@router.post("/detectar")
def detectar(file: UploadFile):
    caminho = os.path.join(UPLOAD_DIR, file.filename)
    with open(caminho, "wb") as f:
        f.write(file.file.read())
    resultado = detectar_doenca(caminho)
    return resultado