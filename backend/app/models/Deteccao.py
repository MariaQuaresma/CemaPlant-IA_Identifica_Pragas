from datetime import datetime
from sqlalchemy import Column, Integer, Float, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Deteccao(Base):
    __tablename__ = "deteccoes"
    id = Column(Integer, primary_key=True, index=True)
    imagem_id = Column(Integer, ForeignKey("imagens.id"))
    planta_id = Column(Integer, ForeignKey("plantas.id"))
    doenca_id = Column(Integer, ForeignKey("doencas.id"))
    porcentagem_confianca = Column(Float)
    data_deteccao = Column(TIMESTAMP, default=datetime.utcnow)
    imagem = relationship("Imagem", back_populates="deteccoes")
    doenca = relationship("Doenca", back_populates="deteccoes")
    recomendacoes = relationship("Recomendacao", back_populates="deteccao")