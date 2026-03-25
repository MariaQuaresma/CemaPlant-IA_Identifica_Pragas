import json
from app.database import SessionLocal

from app.models.Doenca import Doenca
from app.models.Deteccao import Deteccao
from app.models.Imagem import Imagem
from app.models.Planta import Planta
from app.models.Usuario import Usuario
from app.models.Recomendacao import Recomendacao

CLASS_PATH = "app/IA/class_names.json"

def popular_doencas():
    db = SessionLocal()

    with open(CLASS_PATH, "r") as f:
        class_names = json.load(f)

    for nome in class_names:
        existe = db.query(Doenca).filter(Doenca.nome == nome).first()
        
        if not existe:
            nova = Doenca(nome=nome)
            db.add(nova)

    db.commit()
    db.close()

    print("Doenças cadastradas com sucesso!")

if __name__ == "__main__":
    popular_doencas()