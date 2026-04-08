import numpy as np
from PIL import Image
import json
import tensorflow as tf
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "modelo_doencas.h5")
CLASS_PATH = os.path.join(BASE_DIR, "class_names.json")

model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_PATH, "r") as f:
    class_names = json.load(f)

def prever_doenca(caminho_imagem):
    try:
        img = Image.open(caminho_imagem).convert("RGB")
        img = img.resize((224, 224))

        img_array = np.array(img)

        # validação simples
        if img_array.mean() < 30:
            raise ValueError("Imagem muito escura")

        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        pred = model.predict(img_array, verbose=0)

        classe_id = int(np.argmax(pred))
        confianca = float(np.max(pred))

        classe_nome = class_names[classe_id]

        return classe_nome, confianca  

    except Exception as e:
        raise Exception(f"Erro na predição: {str(e)}")