import numpy as np
from PIL import Image
import os
from app.IA.predict import prever_doenca

def predizer_doenca(caminho_imagem: str) -> tuple[str, float]:
    try:
        if not os.path.exists(caminho_imagem):
            raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}") 
        resultado = prever_doenca(caminho_imagem)
        img = Image.open(caminho_imagem).convert("RGB")
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        print(f"[IA] Imagem processada: {img_array.shape}")
        classe_nome, confianca = resultado
        print(f"[IA] Doença detectada: {classe_nome} ({confianca * 100:.2f}%)")
        return classe_nome, float(confianca)
    except Image.UnidentifiedImageError:
        raise ValueError(f"Arquivo não é uma imagem válida: {caminho_imagem}")
    except Exception as e:
        raise Exception(f"Erro ao processar imagem: {str(e)}")