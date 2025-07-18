from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Numeric, func, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from ..database import Base

if TYPE_CHECKING:
    from .pelanggan import Pelanggan
    from .paket_layanan import PaketLayanan

class HargaLayanan(Base):
    __tablename__ = 'harga_layanan'

    id_brand: Mapped[str] = mapped_column(String(191), primary_key=True)
    brand: Mapped[str] = mapped_column(String(191), nullable=False)
    pajak: Mapped[float] = mapped_column(Numeric(5, 2), default=11.00)

    xendit_key_name: Mapped[str] = mapped_column(String(50), nullable=False, server_default="JAKINET")
    
    pelanggan: Mapped[List["Pelanggan"]] = relationship(back_populates="harga_layanan")
    paket_layanan: Mapped[List["PaketLayanan"]] = relationship(
        back_populates="brand", cascade="all, delete-orphan"
    )