from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.database import SessionLocal
from app.models.Doenca import Doenca
from app.models.Planta import Planta
from app.schemas.Deteccao_schema import DeteccaoComRecomendacaoRead
from app.services.doenca_service import predizer_doenca
from app.services.deteccao_service import salvar_deteccao, listar_deteccoes_por_usuario, buscar_deteccao_por_id, listar_todas_deteccoes
from app.services.recomendacao_service import gerar_recomendacao_por_deteccao, criar_recomendacao
from app.services.imagem_service import criar_imagem
import os
import uuid
from app.auth.authentication import get_usuario_logado
from app.IA.predict import prever_imagem

router = APIRouter(prefix="/deteccoes", tags=["deteccoes"])

UPLOAD_DIR = "app/uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAPA_PLANTA_DOENCAS = {
    "Apple": ["Apple_scab", "Black_rot", "Cedar_apple_rust", "healthy"],
    "Blueberry": ["healthy"],
    "Cherry": ["Powdery_mildew", "healthy"],
    "Corn": ["Cercospora_leaf_spot Gray_leaf_spot", "Common_rust_", "Northern_Leaf_Blight", "healthy"],
    "Grape": ["Black_rot", "Esca_(Black_Measles)", "Leaf_blight_(Isariopsis_Leaf_Spot)", "healthy"],
    "Orange": ["Haunglongbing_(Citrus_greening)"],
    "Peach": ["Bacterial_spot", "healthy"],
    "Pepper": ["Bacterial_spot", "healthy"],
    "Potato": ["Early_blight", "Late_blight", "healthy"],
    "Raspberry": ["healthy"],
    "Soybean": ["healthy"],
    "Squash": ["Powdery_mildew"],
    "Strawberry": ["Leaf_scorch", "healthy"],
    "Tomato": [
        "Bacterial_spot", "Early_blight", "Late_blight", "Leaf_Mold",
        "Septoria_leaf_spot", "Spider_mites Two-spotted_spider_mite",
        "Target_Spot", "Tomato_Yellow_Leaf_Curl_Virus",
        "Tomato_mosaic_virus", "healthy"
    ]
}

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
        classe_nome, confianca = prever_imagem(caminho)
        print(f"[IA] Resultado: {classe_nome} ({confianca:.4f})")
        if confianca < 0.4:
            raise HTTPException(
                status_code=400,
                detail="Baixa confiança. Envie uma imagem mais nítida da folha."
            )
        partes = classe_nome.split("___")
        if len(partes) != 2:
            raise HTTPException(status_code=500, detail="Erro ao interpretar resultado da IA")
        planta_nome = partes[0]
        doenca_nome = partes[1]
        planta_nome = planta_nome.replace("_(including_sour)", "").replace(",_bell", "").strip()
        doencas_validas = MAPA_PLANTA_DOENCAS.get(planta_nome)
        if not doencas_validas:
            raise HTTPException(
                status_code=400,
                detail=f"Planta não reconhecida: {planta_nome}"
            )
        if doenca_nome not in doencas_validas:
            print(f"Inconsistência detectada: {planta_nome} x {doenca_nome}")
            raise HTTPException(
                status_code=400,
                detail=f"Inconsistência detectada: {planta_nome} não possui {doenca_nome}"
            )
        if doenca_nome == "healthy" and confianca < 0.6:
            raise HTTPException(
                status_code=400,
                detail="Modelo não tem certeza se a planta está saudável."
            )
        nome_planta_ia = planta_nome.replace("_", " ").strip()
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

@router.get("/usuario", response_model=list[DeteccaoComRecomendacaoRead])
def listar_deteccoes_usuario(usuario=Depends(get_usuario_logado)):
    try:
        deteccoes = listar_deteccoes_por_usuario(usuario.id)
        return [
            {
                "id": d.id,
                "imagem_id": d.imagem_id,
                "planta_id": d.planta_id,
                "doenca_id": d.doenca_id,
                "porcentagem_confianca": d.porcentagem_confianca,
                "data_deteccao": d.data_deteccao,
                "recomendacao": d.recomendacoes[0].texto_recomendacao if d.recomendacoes else None
            }
            for d in deteccoes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/todas", response_model=list[DeteccaoComRecomendacaoRead])
def todas_deteccoes(usuario=Depends(get_usuario_logado)):
    try:
        deteccoes = listar_todas_deteccoes()
        return [
            {
                "id": d.id,
                "imagem_id": d.imagem_id,
                "planta_id": d.planta_id,
                "doenca_id": d.doenca_id,
                "porcentagem_confianca": d.porcentagem_confianca,
                "data_deteccao": d.data_deteccao,
                "recomendacao": d.recomendacoes[0].texto_recomendacao if d.recomendacoes else None
            }
            for d in deteccoes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{deteccao_id}", response_model=DeteccaoComRecomendacaoRead)
def buscar_deteccao(deteccao_id: int, usuario=Depends(get_usuario_logado)):
    try:
        deteccao = buscar_deteccao_por_id(deteccao_id)
        if not deteccao:
            raise HTTPException(status_code=404, detail="Detecção não encontrada")
        return {
            "id": deteccao.id,
            "imagem_id": deteccao.imagem_id,
            "planta_id": deteccao.planta_id,
            "doenca_id": deteccao.doenca_id,
            "porcentagem_confianca": deteccao.porcentagem_confianca,
            "data_deteccao": deteccao.data_deteccao,
            "recomendacao": deteccao.recomendacoes[0].texto_recomendacao if deteccao.recomendacoes else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))