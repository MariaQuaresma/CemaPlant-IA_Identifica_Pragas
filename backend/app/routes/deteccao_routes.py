from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.database import SessionLocal
from app.models.Doenca import Doenca
from app.models.Planta import Planta
from app.schemas.Deteccao_schema import DeteccaoComRecomendacaoRead
from app.services.doenca_service import predizer_doenca
from app.services.deteccao_service import salvar_deteccao
from app.services.recomendacao_service import gerar_recomendacao_por_deteccao, criar_recomendacao
from app.services.imagem_service import criar_imagem
import os
import uuid
from app.auth.authentication import get_usuario_logado

router = APIRouter(prefix="/deteccoes", tags=["deteccoes"])

UPLOAD_DIR = "app/uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=DeteccaoComRecomendacaoRead)
def detectar_doenca(file: UploadFile = File(...), usuario=Depends(get_usuario_logado)):
    db = SessionLocal()
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
        filename = f"{uuid.uuid4()}_{file.filename}"
        caminho = os.path.join(UPLOAD_DIR, filename)
        with open(caminho, "wb") as f:
            f.write(file.file.read())
        imagem = criar_imagem(usuario.id, caminho)
        classe_nome, confianca = predizer_doenca(caminho)
        print(f"[IA] Resultado: {classe_nome} ({confianca:.4f})")
        if confianca < 0.4:
            raise HTTPException(
                status_code=400,
                detail="Baixa confiança. Envie uma imagem mais nítida da folha."
            )
        if "healthy" in classe_nome.lower() and confianca < 0.6:
            raise HTTPException(
                status_code=400,
                detail="Modelo não tem certeza se a planta está saudável. Tente outra imagem."
            )
        nome_planta_ia = classe_nome.split("___")[0].replace("_", " ").strip()
        planta = db.query(Planta).filter(Planta.nome == nome_planta_ia).first()
        if not planta:
            planta = Planta(
                nome=nome_planta_ia,
                nome_cientifico=None,
                descricao=f"Planta identificada automaticamente: {nome_planta_ia}"
            )
            db.add(planta)
            db.commit()
            db.refresh(planta)
        doenca = db.query(Doenca).filter(Doenca.nome == classe_nome).first()
        if not doenca:
            raise HTTPException(status_code=404, detail="Doença não cadastrada no banco")
        deteccao = salvar_deteccao(
            imagem.id,
            planta.id,
            doenca.id,
            confianca
        )
        texto_recomendacao = gerar_recomendacao_por_deteccao(deteccao.id)
        criar_recomendacao(deteccao.id, texto_recomendacao)
        return {
            "id": deteccao.id,
            "imagem_id": deteccao.imagem_id,
            "planta_id": deteccao.planta_id,
            "doenca_id": deteccao.doenca_id,
            "porcentagem_confianca": deteccao.porcentagem_confianca,
            "data_deteccao": deteccao.data_deteccao,
            "recomendacao": texto_recomendacao,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )
    finally:
        db.close()