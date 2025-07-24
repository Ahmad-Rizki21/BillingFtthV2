from pydantic import BaseModel
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
class DataTeknisCreate(DataTeknisBase):
    pass

# Skema untuk membaca data (response)
class DataTeknis(DataTeknisBase):
    id: int

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
    onu_power: Optional[int] = None
    
    # --- INI BAGIAN YANG PERLU DIPASTIKAN ---
    # Pastikan mikrotik_server_id juga Optional
    mikrotik_server_id: Optional[int] = None

    class Config:
        from_attributes = True
