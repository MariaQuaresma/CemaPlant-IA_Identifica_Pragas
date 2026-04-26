import numpy as np
from PIL import Image, UnidentifiedImageError
import json
import tensorflow as tf
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PLANTA_PATH = os.path.join(BASE_DIR, "modelo_plantas.keras")
MODEL_DOENCA_PATH = os.path.join(BASE_DIR, "modelo_doencas.keras")
CLASS_PLANTA_PATH = os.path.join(BASE_DIR, "class_names_plantas.json")
CLASS_DOENCA_PATH = os.path.join(BASE_DIR, "class_names_doencas.json")

model_planta = tf.keras.models.load_model(MODEL_PLANTA_PATH)
model_doenca = tf.keras.models.load_model(MODEL_DOENCA_PATH)

with open(CLASS_PLANTA_PATH, "r") as f:
    classes_plantas = json.load(f)
with open(CLASS_DOENCA_PATH, "r") as f:
    classes_doencas = json.load(f)

IMG_SIZE = 224

DOENCA_PREFIXO_PARA_PLANTA = {
    "Cherry_(including_sour)": "Cherry",
    "Corn_(maize)":            "Corn",
    "Pepper,_bell":            "Pepper",
}

PLANTA_PARA_DOENCA_PREFIXO = {
    "Cherry": "Cherry_(including_sour)",
    "Corn":   "Corn_(maize)",
    "Pepper": "Pepper,_bell",
}

ALIASES_NOME_DOENCA = {
    "Leaf_Molde": "Leaf_Mold",
}


PLANTAS_POUCOS_DADOS = {"Blueberry", "Raspberry", "Soybean", "Orange", "Cherry"}

INDICES_DOENCA_POR_PLANTA: dict[str, list[int]] = {}
for idx, classe_doenca in enumerate(classes_doencas):
    prefixo_doenca = classe_doenca.split("___", 1)[0]
    planta = DOENCA_PREFIXO_PARA_PLANTA.get(prefixo_doenca, prefixo_doenca)
    INDICES_DOENCA_POR_PLANTA.setdefault(planta, []).append(idx)


def preprocess(img: Image.Image) -> np.ndarray:
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(img).astype(np.float32)
    img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
    return np.expand_dims(img_array, axis=0)


def _normalizar_nome_doenca(doenca_nome: str) -> str:
    return ALIASES_NOME_DOENCA.get(doenca_nome, doenca_nome)


def _prefixo_doenca_para_nome_planta(prefixo: str) -> str:
    """Converte prefixo do modelo de doenças para nome no modelo de plantas."""
    return DOENCA_PREFIXO_PARA_PLANTA.get(prefixo, prefixo)


def _nome_planta_para_prefixo_doenca(planta: str) -> str:
    """Converte nome do modelo de plantas para prefixo usado no modelo de doenças."""
    return PLANTA_PARA_DOENCA_PREFIXO.get(planta, planta)


def _extrair_top_doenca_por_planta(pred_doenca: np.ndarray, planta_nome: str):
    """Retorna a melhor doença dentro das classes permitidas para essa planta."""
    indices = INDICES_DOENCA_POR_PLANTA.get(planta_nome, [])
    if not indices:
        idx = int(np.argmax(pred_doenca[0]))
        return classes_doencas[idx], float(pred_doenca[0][idx]), None, 0.0
    logits = pred_doenca[0][indices]
    ordem  = np.argsort(logits)[::-1]
    idx_top  = indices[int(ordem[0])]
    conf_top = float(pred_doenca[0][idx_top])
    if len(ordem) > 1:
        idx_seg  = indices[int(ordem[1])]
        nome_seg = classes_doencas[idx_seg]
        conf_seg = float(pred_doenca[0][idx_seg])
    else:
        nome_seg = None
        conf_seg = 0.0
    return classes_doencas[idx_top], conf_top, nome_seg, conf_seg

def _selecionar_par_por_doenca(pred_planta: np.ndarray, pred_doenca: np.ndarray):
    """
    Para cada uma das top-5 doenças, verifica se a planta correspondente
    está no top-3 do modelo de plantas. Escolhe o par com melhor score.
    """
    top5_doenca_ids = np.argsort(pred_doenca[0])[-5:][::-1]
    top3_planta_ids = np.argsort(pred_planta[0])[-3:][::-1]
    top3_plantas    = {classes_plantas[i] for i in top3_planta_ids}

    melhor_par   = None
    melhor_score = -1.0

    for doenca_id in top5_doenca_ids:
        doenca_completa  = classes_doencas[doenca_id]
        conf_doenca      = float(pred_doenca[0][doenca_id])
        prefixo_doenca   = doenca_completa.split("___", 1)[0]
    
        planta_da_doenca = _prefixo_doenca_para_nome_planta(prefixo_doenca)

        if planta_da_doenca not in classes_plantas:
            continue
        planta_id   = classes_plantas.index(planta_da_doenca)
        conf_planta = float(pred_planta[0][planta_id])

        bonus = 0.15 if planta_da_doenca in top3_plantas else 0.0
        score = (conf_doenca * 0.6 + conf_planta * 0.4) + bonus
        if score > melhor_score:
            melhor_score = score
            melhor_par   = (planta_da_doenca, conf_planta, doenca_completa, conf_doenca)

    if melhor_par is None:
        doenca_id       = int(np.argmax(pred_doenca[0]))
        doenca_completa = classes_doencas[doenca_id]
        conf_doenca     = float(pred_doenca[0][doenca_id])
        prefixo         = doenca_completa.split("___", 1)[0]
        planta_nome     = _prefixo_doenca_para_nome_planta(prefixo)
        if planta_nome in classes_plantas:
            planta_id   = classes_plantas.index(planta_nome)
            conf_planta = float(pred_planta[0][planta_id])
        else:
            planta_id   = int(np.argmax(pred_planta[0]))
            conf_planta = float(np.max(pred_planta[0]))
        melhor_par = (planta_nome, conf_planta, doenca_completa, conf_doenca)
    return melhor_par

def _ajustar_tomato_por_indicio(pred_planta, pred_doenca,
                                 planta_nome, conf_planta,
                                 doenca_completa, conf_doenca):
    if "Tomato" not in classes_plantas:
        return planta_nome, conf_planta, doenca_completa, conf_doenca
    idx_tomato       = classes_plantas.index("Tomato")
    conf_tomato_pl   = float(pred_planta[0][idx_tomato])
    top5_ids         = np.argsort(pred_doenca[0])[-5:][::-1]
    qtde_tomato_top5 = sum(
        1 for i in top5_ids if classes_doencas[i].startswith("Tomato___")
    )
    ha_indicio = (
        planta_nome == "Tomato"
        or doenca_completa.startswith("Tomato___")
        or conf_tomato_pl >= 0.35
        or qtde_tomato_top5 >= 2
    )
    if not ha_indicio:
        return planta_nome, conf_planta, doenca_completa, conf_doenca
    melhor_tomato, conf_mt, segundo_tomato, conf_st = _extrair_top_doenca_por_planta(
        pred_doenca, "Tomato"
    )
    if (melhor_tomato == "Tomato___healthy"
            and segundo_tomato is not None
            and conf_st >= 0.12
            and (conf_mt - conf_st) <= 0.65):
        melhor_tomato = segundo_tomato
        conf_mt       = conf_st
    return "Tomato", max(conf_planta, conf_tomato_pl), melhor_tomato, conf_mt

def _ajustar_tomato_falso_healthy(pred_doenca, doenca_completa, conf_doenca):
    if doenca_completa != "Tomato___healthy":
        return doenca_completa, conf_doenca
    foco = {"Tomato___Leaf_Mold", "Tomato___Target_Spot", "Tomato___Septoria_leaf_spot"}
    top8 = np.argsort(pred_doenca[0])[-8:][::-1]
    melhor_foco, melhor_conf_foco = None, 0.0
    for idx in top8:
        nome = classes_doencas[idx]
        if nome in foco:
            conf = float(pred_doenca[0][idx])
            if conf > melhor_conf_foco:
                melhor_conf_foco = conf
                melhor_foco      = nome
    if melhor_foco and melhor_conf_foco >= 0.20 and (conf_doenca - melhor_conf_foco) <= 0.18:
        return melhor_foco, melhor_conf_foco
    return doenca_completa, conf_doenca

def prever_imagem(caminho_imagem: str):
    try:
        if not os.path.exists(caminho_imagem):
            raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}")
        img       = Image.open(caminho_imagem).convert("RGB")
        img_array = preprocess(img)

        pred_planta = model_planta.predict(img_array, verbose=0)
        pred_doenca = model_doenca.predict(img_array, verbose=0)

        planta_nome, conf_planta, doenca_completa, conf_doenca = \
            _selecionar_par_por_doenca(pred_planta, pred_doenca)

        planta_nome, conf_planta, doenca_completa, conf_doenca = \
            _ajustar_tomato_por_indicio(
                pred_planta, pred_doenca,
                planta_nome, conf_planta,
                doenca_completa, conf_doenca
            )
        doenca_completa, conf_doenca = _ajustar_tomato_falso_healthy(
            pred_doenca, doenca_completa, conf_doenca
        )

        partes      = doenca_completa.split("___", 1)
        doenca_nome = _normalizar_nome_doenca(partes[1] if len(partes) == 2 else doenca_completa)
        resultado   = f"{planta_nome}___{doenca_nome}"

        if planta_nome in PLANTAS_POUCOS_DADOS:
            confianca_final = conf_doenca
        else:
            confianca_final = conf_doenca * 0.65 + conf_planta * 0.35

        print(f"[IA] Planta:          {planta_nome} ({conf_planta:.4f})")
        print(f"[IA] Doença:          {doenca_nome} ({conf_doenca:.4f})")
        print(f"[IA] Confiança Final: {confianca_final:.4f}")
        return resultado, confianca_final

    except UnidentifiedImageError:
        raise Exception("Arquivo enviado não é uma imagem válida")
    except Exception as e:
        raise Exception(f"Erro na predição: {str(e)}")