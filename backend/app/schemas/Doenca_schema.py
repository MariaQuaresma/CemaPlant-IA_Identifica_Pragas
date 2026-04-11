from pydantic import BaseModel
from typing import Optional

class DoencaBase(BaseModel):
    nome: str
    nome_cientifico: Optional[str] = None
    descricao: Optional[str] = None
    nivel: Optional[int] = None

class DoencaCreate(DoencaBase):
    pass

class DoencaRead(DoencaBase):
    id: int

    class Config:
        from_attributes = True