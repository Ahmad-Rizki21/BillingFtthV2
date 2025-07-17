from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import String, BigInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column
from ..database import Base

# Impor tabel perantara
from .role_has_permissions import role_has_permissions

if TYPE_CHECKING:
    from .role import Role

class Permission(Base):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(191), unique=True, nullable=False)

    # PASTIKAN back_populates menunjuk ke 'permissions' (nama relasi di model Role)
    roles: Mapped[List["Role"]] = relationship(
        secondary=role_has_permissions,
        back_populates="permissions"
    )
