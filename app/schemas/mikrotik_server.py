# app/schemas/mikrotik_server.py
from pydantic import BaseModel
from typing import Optional

# Skema dasar untuk Mikrotik Server
class MikrotikServerBase(BaseModel):
    name: str
    host_ip: str
    username: str
    password: str
    port: int
    ros_version: Optional[str] = None
    is_active: bool = True
    last_connection_status: Optional[str] = None
    last_connected_at: Optional[str] = None

# Skema untuk membuat Mikrotik Server baru
class MikrotikServerCreate(MikrotikServerBase):
    pass

# Skema untuk membaca data (response)
class MikrotikServer(MikrotikServerBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True

# Skema untuk pembaruan parsial
class MikrotikServerUpdate(BaseModel):
    name: Optional[str] = None
    host_ip: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    port: Optional[int] = None
    ros_version: Optional[str] = None
    is_active: Optional[bool] = None
    last_connection_status: Optional[str] = None
    last_connected_at: Optional[str] = None

    class Config:
        from_attributes = True