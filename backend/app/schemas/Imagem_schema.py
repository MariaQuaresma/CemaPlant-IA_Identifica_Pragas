from pydantic import BaseModel, field_serializer
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Optional

try:
    TZ_BRASILIA = ZoneInfo("America/Sao_Paulo")
except ZoneInfoNotFoundError:
    TZ_BRASILIA = timezone.utc

class ImagemBase(BaseModel):
    usuario_id: int
    url_imagem: str

class ImagemCreate(ImagemBase):
    pass

class ImagemRead(ImagemBase):
    id: int
    data_upload: datetime

    @field_serializer("data_upload")
    def serialize_data_upload(self, value: datetime):
        data = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return data.astimezone(TZ_BRASILIA)

    class Config:
        from_attributes = True