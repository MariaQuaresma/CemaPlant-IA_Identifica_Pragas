from pydantic import BaseModel, EmailStr, field_serializer
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Optional

try:
    TZ_BRASILIA = ZoneInfo("America/Sao_Paulo")
except ZoneInfoNotFoundError:
    TZ_BRASILIA = timezone(timedelta(hours=-3), name="BRT")

class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class UsuarioRead(UsuarioBase):
    id: int
    data_criacao: datetime

    @field_serializer("data_criacao")
    def serialize_data_criacao(self, value: datetime):
        data = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return data.astimezone(TZ_BRASILIA).isoformat()

    class Config:
        from_attributes = True