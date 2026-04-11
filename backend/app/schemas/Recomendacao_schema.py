from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RecomendacaoBase(BaseModel):
    deteccao_id: int
    texto_recomendacao: str

class RecomendacaoCreate(RecomendacaoBase):
    pass

class RecomendacaoRead(RecomendacaoBase):
    id: int
    data_criacao: datetime

    class Config:
        from_attributes = True
