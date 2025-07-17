from pydantic import BaseModel
from typing import Optional
from datetime import date

class LanggananBase(BaseModel):
    pelanggan_id: int
    paket_layanan_id: int 
    tanggal_mulai: date
    status: str = 'aktif'

class LanggananCreate(BaseModel):
    pelanggan_id: int
    paket_layanan_id: int

class LanggananUpdate(BaseModel):
    paket_layanan_id: Optional[int] = None
    status: Optional[str] = None

class Langganan(LanggananBase):
    id: int
    class Config:
        from_attributes = True