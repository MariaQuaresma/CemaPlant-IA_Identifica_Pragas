from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class ImagemBase(BaseModel):
    usuario_id: int
    url_imagem: str

class ImagemCreate(ImagemBase):
    pass

class ImagemRead(ImagemBase):
    id: int
    data_upload: datetime

    class Config:
        from_attributes = True