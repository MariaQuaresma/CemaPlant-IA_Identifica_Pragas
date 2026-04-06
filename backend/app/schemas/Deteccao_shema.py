from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DeteccaoBase(BaseModel):
    imagem_id: int
    planta_id: int
    doenca_id: int
    porcentagem_confianca: float

class DeteccaoCreate(DeteccaoBase):
    pass

class DeteccaoRead(DeteccaoBase):
    id: int
    data_deteccao: datetime

    class Config:
        from_attributes = True

class DeteccaoComRecomendacaoRead(DeteccaoRead):
    recomendacao: Optional[str] = None