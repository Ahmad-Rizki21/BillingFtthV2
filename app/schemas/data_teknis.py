from pydantic import BaseModel, Field
from typing import Optional


# Skema dasar untuk data teknis
class DataTeknisBase(BaseModel):
    pelanggan_id: int
    id_vlan: str
    id_pelanggan: str
    password_pppoe: str
    ip_pelanggan: str
    profile_pppoe: str
    olt: str
    olt_custom: Optional[str] = None
    pon: int
    otb: int
    odc: int
    odp: int
    speedtest_proof: Optional[str] = None
    onu_power: int


# Skema untuk membuat data teknis baru
class DataTeknisCreate(BaseModel):
    # Field yang WAJIB diisi oleh tim NOC
    pelanggan_id: int
    id_pelanggan: str
    password_pppoe: str
    mikrotik_server_id: int
    olt: str

    # Field yang OPSIONAL saat pembuatan
    id_vlan: Optional[str] = None
    ip_pelanggan: Optional[str] = None
    profile_pppoe: Optional[str] = "default-profile"
    olt_custom: Optional[str] = None

    # Field yang akan diisi teknisi, diberi nilai default 0
    # Penggunaan Field() sudah benar setelah di-impor
    pon: int = Field(default=0)
    otb: int = Field(default=0)
    odc: int = Field(default=0)
    odp: int = Field(default=0)
    onu_power: float = Field(default=0.0)
    sn: Optional[str] = None


# Skema untuk membaca data (response)
class DataTeknis(BaseModel):
    id: int
    pelanggan_id: int
    id_pelanggan: str
    password_pppoe: str
    mikrotik_server_id: Optional[int] = None
    olt: Optional[str] = None
    id_vlan: Optional[str] = None
    ip_pelanggan: Optional[str] = None
    profile_pppoe: Optional[str] = None
    olt_custom: Optional[str] = None
    pon: Optional[int] = None
    otb: Optional[int] = None
    odc: Optional[int] = None
    odp: Optional[int] = None
    onu_power: Optional[float] = None
    sn: Optional[str] = None
    speedtest_proof: Optional[str] = None

    class Config:
        from_attributes = True


# Skema untuk pembaruan parsial (semua field opsional)
class DataTeknisUpdate(BaseModel):
    pelanggan_id: Optional[int] = None
    id_vlan: Optional[str] = None
    id_pelanggan: Optional[str] = None
    password_pppoe: Optional[str] = None
    ip_pelanggan: Optional[str] = None
    profile_pppoe: Optional[str] = None
    olt: Optional[str] = None
    olt_custom: Optional[str] = None
    pon: Optional[int] = None
    otb: Optional[int] = None
    odc: Optional[int] = None
    odp: Optional[int] = None
    speedtest_proof: Optional[str] = None
    sn: Optional[str] = None
    onu_power: Optional[int] = None

    class Config:
        from_attributes = True


# Skema khusus untuk validasi data dari file import Excel
class DataTeknisImport(BaseModel):
    email_pelanggan: str
    id_vlan: str
    id_pelanggan: str
    password_pppoe: str
    ip_pelanggan: str
    profile_pppoe: str
    olt: str
    olt_custom: Optional[str] = None
    pon: Optional[int] = None
    otb: Optional[int] = None
    odc: Optional[int] = None
    odp: Optional[int] = None
    sn: Optional[str] = None
    onu_power: Optional[int] = None

    # --- INI BAGIAN YANG PERLU DIPASTIKAN ---
    # Pastikan mikrotik_server_id juga Optional
    mikrotik_server_id: Optional[int] = None

    class Config:
        from_attributes = True
