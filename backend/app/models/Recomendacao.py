from datetime import datetime
from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Recomendacao(Base):
    __tablename__ = "recomendacoes"
    id = Column(Integer, primary_key=True, index=True)
    deteccao_id = Column(Integer, ForeignKey("deteccoes.id"))
    texto_recomendacao = Column(Text)
    data_criacao = Column(TIMESTAMP, default=datetime.utcnow)
    deteccao = relationship("Deteccao", back_populates="recomendacoes")