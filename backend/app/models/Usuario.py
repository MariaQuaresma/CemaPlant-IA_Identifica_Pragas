from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    senha = Column(String, nullable=False)
    data_criacao = Column(TIMESTAMP, default=datetime.utcnow)