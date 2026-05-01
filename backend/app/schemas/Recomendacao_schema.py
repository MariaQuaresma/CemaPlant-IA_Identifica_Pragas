from pydantic import BaseModel, field_serializer
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Optional

try:
    TZ_BRASILIA = ZoneInfo("America/Sao_Paulo")
except ZoneInfoNotFoundError:
    TZ_BRASILIA = timezone(timedelta(hours=-3), name="BRT")

class RecomendacaoBase(BaseModel):
    deteccao_id: int
    texto_recomendacao: str

class RecomendacaoCreate(RecomendacaoBase):
    pass

class RecomendacaoRead(RecomendacaoBase):
    id: int
    data_criacao: datetime

    @field_serializer("data_criacao")
    def serialize_data_criacao(self, value: datetime):
        data = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return data.astimezone(TZ_BRASILIA).isoformat()

    class Config:
        from_attributes = True
