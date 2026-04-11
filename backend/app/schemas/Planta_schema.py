from pydantic import BaseModel
from typing import Optional

class PlantaBase(BaseModel):
    nome: str
    nome_cientifico: Optional[str] = None
    descricao: Optional[str] = None

class PlantaCreate(PlantaBase):
    pass

class PlantaRead(PlantaBase):
    id: int

    class Config:
        from_attributes = True