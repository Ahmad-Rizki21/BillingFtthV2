from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

# Skema untuk membuat Pelanggan baru
class PelangganCreate(BaseModel):
    no_ktp: str
    nama: str
    alamat: str
    alamat_2: Optional[str] = None
    tgl_instalasi: Optional[date] = None
    blok: str
    unit: str
    no_telp: str
    email: EmailStr
    id_brand: Optional[str] = None
    layanan: Optional[str] = None

    class Config:
        from_attributes = True

# Skema untuk menampilkan data Pelanggan
class Pelanggan(PelangganCreate):
    id: int

# Skema untuk pembaruan parsial (semua field opsional)
class PelangganUpdate(BaseModel):
    no_ktp: Optional[str] = None
    nama: Optional[str] = None
    alamat: Optional[str] = None
    alamat_2: Optional[str] = None
    tgl_instalasi: Optional[date] = None
    blok: Optional[str] = None
    unit: Optional[str] = None
    no_telp: Optional[str] = None
    email: Optional[EmailStr] = None
    id_brand: Optional[str] = None
    layanan: Optional[str] = None

    class Config:
        from_attributes = True