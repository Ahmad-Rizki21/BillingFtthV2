from pydantic import BaseModel
from typing import Optional, List
from .user import User as UserSchema # Impor skema User untuk relasi

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None

class Role(RoleBase):
    id: int
    class Config:
        from_attributes = True

# Skema tambahan untuk menampilkan role beserta user di dalamnya
class RoleWithUsers(Role):
    users: List[UserSchema] = []
