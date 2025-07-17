from pydantic import BaseModel
from typing import Optional

class HargaLayananBase(BaseModel):
    id_brand: str
    brand: str
    pajak: float = 11.00

class HargaLayananCreate(HargaLayananBase):
    pass

class HargaLayananUpdate(BaseModel):
    brand: Optional[str] = None
    pajak: Optional[float] = None

class HargaLayanan(HargaLayananBase):
    class Config:
        from_attributes = True