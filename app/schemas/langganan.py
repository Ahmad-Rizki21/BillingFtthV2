from pydantic import BaseModel
from typing import Optional
from datetime import date
from .paket_layanan import PaketLayanan

from .pelanggan import PelangganInLangganan 

class LanggananBase(BaseModel):
    id: int
    pelanggan_id: int
    paket_layanan_id: int

    metode_pembayaran: str
    harga_awal: float | None

    status: str
    tgl_jatuh_tempo: date | None = None
    tgl_invoice_terakhir: date | None = None


class LanggananCreate(BaseModel):
    pelanggan_id: int
    paket_layanan_id: int
    status: str
    metode_pembayaran: str
    harga_awal: Optional[float] = None
    tgl_jatuh_tempo: Optional[date] = None
    tgl_invoice_terakhir: Optional[date] = None

class LanggananUpdate(BaseModel):
    paket_layanan_id: Optional[int] = None
    status: Optional[str] = None
    tgl_jatuh_tempo: Optional[date] = None 
    metode_pembayaran: Optional[str] = None
    harga_awal: Optional[float] = None

class Langganan(LanggananBase):
    id: int
    paket_layanan: PaketLayanan
    class Config:
        from_attributes = True

class LanggananImport(BaseModel):
    email_pelanggan: str
    id_brand: str
    nama_paket_layanan: str
    status: str = 'Aktif'
    metode_pembayaran: str = 'Otomatis'
    tgl_jatuh_tempo: Optional[date] = None

class Langganan(LanggananBase):
    id: int
    paket_layanan: PaketLayanan
    
    # UBAH baris ini
    pelanggan: PelangganInLangganan

    class Config:
        from_attributes = True
