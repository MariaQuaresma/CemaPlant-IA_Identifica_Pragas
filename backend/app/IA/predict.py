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

def preprocess(img: Image.Image):
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(img).astype(np.float32)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def prever_imagem(caminho_imagem: str):
    try:
        if not os.path.exists(caminho_imagem):
            raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}")

        img = Image.open(caminho_imagem).convert("RGB")
        img_array = preprocess(img)

        pred_planta = model_planta.predict(img_array, verbose=0)
        planta_id = int(np.argmax(pred_planta))
        planta_nome = classes_plantas[planta_id]
        conf_planta = float(np.max(pred_planta))

        pred_doenca = model_doenca.predict(img_array, verbose=0)
        doenca_id = int(np.argmax(pred_doenca))
        doenca_nome = classes_doencas[doenca_id]
        conf_doenca = float(np.max(pred_doenca))

        resultado = f"{planta_nome}___{doenca_nome}"
        confianca_final = (conf_planta + conf_doenca) / 2

        print(f"[IA] Planta: {planta_nome} ({conf_planta:.4f})")
        print(f"[IA] Doença: {doenca_nome} ({conf_doenca:.4f})")
        return resultado, confianca_final
    except UnidentifiedImageError:
        raise Exception("Arquivo enviado não é uma imagem válida")
    except Exception as e:
        raise Exception(f"Erro na predição: {str(e)}")