from pydantic import BaseModel
from typing import Optional
from datetime import date
from .paket_layanan import PaketLayanan
from .pelanggan import PelangganInLangganan

# -- Base Schema --
# Berisi field yang sama persis dengan kolom di database
class LanggananBase(BaseModel):
    pelanggan_id: int
    paket_layanan_id: int
    metode_pembayaran: str
    harga_awal: Optional[float] = None
    status: str
    tgl_jatuh_tempo: Optional[date] = None
    tgl_invoice_terakhir: Optional[date] = None
    tgl_mulai_langganan: Optional[date] = None

# -- Schema untuk Membuat Langganan Baru --
class LanggananCreate(BaseModel):
    pelanggan_id: int
    paket_layanan_id: int
    status: str
    metode_pembayaran: str
    tgl_mulai_langganan: Optional[date] = None
    sertakan_bulan_depan: bool = False

# -- Schema untuk Update Langganan --
class LanggananUpdate(BaseModel):
    paket_layanan_id: Optional[int] = None
    status: Optional[str] = None
    tgl_jatuh_tempo: Optional[date] = None
    metode_pembayaran: Optional[str] = None
    harga_awal: Optional[float] = None

# -- Schema untuk Import --
class LanggananImport(BaseModel):
    email_pelanggan: str
    id_brand: str
    nama_paket_layanan: str
    status: str = "Aktif"
    metode_pembayaran: str = "Otomatis"
    tgl_jatuh_tempo: Optional[date] = None

# -- Schema Utama untuk Response API (HANYA ADA SATU INI) --
# Inilah skema yang digunakan untuk menampilkan data ke frontend
class Langganan(LanggananBase):
    id: int
    paket_layanan: PaketLayanan
    pelanggan: PelangganInLangganan

    class Config:
        from_attributes = True