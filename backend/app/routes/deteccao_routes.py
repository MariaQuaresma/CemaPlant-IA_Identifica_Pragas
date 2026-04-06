from fastapi import APIRouter, UploadFile, File, HTTPException
from app.database import SessionLocal
from app.models.Doenca import Doenca
from app.models.Planta import Planta
from app.schemas.Deteccao_shema import DeteccaoComRecomendacaoRead
from app.services.doenca_service import predizer_doenca
from app.services.deteccao_service import salvar_deteccao, listar_deteccoes_por_usuario
from app.services.recomendacao_service import gerar_recomendacao_por_deteccao, criar_recomendacao
from app.services.imagem_service import criar_imagem
import os

router = APIRouter(prefix="/deteccoes", tags=["deteccoes"])
UPLOAD_DIR = "app/uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=DeteccaoComRecomendacaoRead)
def detectar_doenca(usuario_id: int, file: UploadFile = File(...)):
    try:
        caminho = os.path.join(UPLOAD_DIR, file.filename)
        with open(caminho, "wb") as f:
            f.write(file.file.read())
        imagem = criar_imagem(usuario_id, caminho)
        classe_nome, confianca = predizer_doenca(caminho)
        nome_planta_ia = classe_nome.split("___")[0].replace("_", " ")
        db = SessionLocal()
        try:
            nova_planta = Planta(
                nome=nome_planta_ia,
                nome_cientifico=None,
                descricao=f"Planta identificada automaticamente: {nome_planta_ia}"
            )
            db.add(nova_planta)
            db.commit()
            db.refresh(nova_planta)
            doenca = db.query(Doenca).filter(Doenca.nome == classe_nome).first()
            if not doenca:
                raise HTTPException(status_code=404, detail="Doença não cadastrada")
            deteccao = salvar_deteccao(
                imagem.id,
                nova_planta.id,  
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
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar imagem: {str(e)}")

@router.get("/historico/usuario/{usuario_id}", response_model=list[DeteccaoComRecomendacaoRead])
def listar_historico_por_usuario(usuario_id: int):
    try:
        deteccoes = listar_deteccoes_por_usuario(usuario_id)
        historico = []
        for deteccao in deteccoes:
            recomendacao = None
            if deteccao.recomendacoes:
                recomendacao = deteccao.recomendacoes[0].texto_recomendacao
            historico.append({
                "id": deteccao.id,
                "imagem_id": deteccao.imagem_id,
                "planta_id": deteccao.planta_id,
                "doenca_id": deteccao.doenca_id,
                "porcentagem_confianca": deteccao.porcentagem_confianca,
                "data_deteccao": deteccao.data_deteccao,
                "recomendacao": recomendacao,
            })
        return historico
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))