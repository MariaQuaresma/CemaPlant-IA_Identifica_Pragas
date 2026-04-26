from pydantic import BaseModel, field_serializer
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Optional

try:
    TZ_BRASILIA = ZoneInfo("America/Sao_Paulo")
except ZoneInfoNotFoundError:
    TZ_BRASILIA = timezone.utc

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

    @field_serializer("data_deteccao")
    def serialize_data_deteccao(self, value: datetime):
        data = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return data.astimezone(TZ_BRASILIA)

    class Config:
        from_attributes = True

class DeteccaoComRecomendacaoRead(DeteccaoRead):
    recomendacao: Optional[str] = None