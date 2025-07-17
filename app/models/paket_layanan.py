from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import String, BigInteger, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship, Mapped, mapped_column
from ..database import Base

if TYPE_CHECKING:
    from .harga_layanan import HargaLayanan
    from .langganan import Langganan

class PaketLayanan(Base):
    __tablename__ = 'paket_layanan'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_brand: Mapped[str] = mapped_column(ForeignKey('harga_layanan.id_brand'))
    nama_paket: Mapped[str] = mapped_column(String(191))
    kecepatan: Mapped[int] = mapped_column(Integer)
    harga: Mapped[float] = mapped_column(Numeric(15, 2))
    
    brand: Mapped["HargaLayanan"] = relationship(back_populates="paket_layanan")
    langganan: Mapped[List["Langganan"]] = relationship(back_populates="paket_layanan")