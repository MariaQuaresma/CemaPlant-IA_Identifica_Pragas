from datetime import datetime
from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Imagem(Base):
    __tablename__ = "imagens"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    url_imagem = Column(Text, nullable=False)
    data_upload = Column(TIMESTAMP, default=datetime.utcnow)
    deteccoes = relationship("Deteccao", back_populates="imagem")