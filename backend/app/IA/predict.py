import numpy as np
from PIL import Image, UnidentifiedImageError
import json
import tensorflow as tf
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "modelo_doencas.keras")
CLASS_PATH = os.path.join(BASE_DIR, "class_names.json")

model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_PATH, "r") as f:
    class_names = json.load(f)

IMG_SIZE = 224

def preprocess(img: Image.Image):
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(img).astype(np.float32)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def prever_doenca(caminho_imagem: str):
    try:
        if not os.path.exists(caminho_imagem):
            raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}")
        img = Image.open(caminho_imagem).convert("RGB")
        img_array = preprocess(img)
        pred = model.predict(img_array, verbose=0)
        if pred is None or len(pred) == 0:
            raise ValueError("Modelo retornou predição vazia")
        classe_id = int(np.argmax(pred))
        confianca = float(np.max(pred))
        if classe_id >= len(class_names):
            raise ValueError("Classe prevista fora do range")
        classe_nome = class_names[classe_id]
        print(f"[IA] Classe: {classe_nome} | Confiança: {confianca:.4f}")
        return classe_nome, confianca
    except UnidentifiedImageError:
        raise Exception("Arquivo enviado não é uma imagem válida")
    except Exception as e:
        raise Exception(f"Erro na predição: {str(e)}")