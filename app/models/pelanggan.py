from __future__ import annotations
from typing import List, TYPE_CHECKING
from datetime import date

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import String, Date, Text, ForeignKey, BigInteger
from ..database import Base

if TYPE_CHECKING:
    from .data_teknis import DataTeknis
    from .langganan import Langganan
    from .harga_layanan import HargaLayanan
    from .invoice import Invoice  # Tambahkan import Invoice

class Pelanggan(Base):
    __tablename__ = 'pelanggan'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    
    no_ktp: Mapped[str] = mapped_column(String(191), nullable=False)
    nama: Mapped[str] = mapped_column(String(191), nullable=False)
    alamat: Mapped[str] = mapped_column(String(191), nullable=False)
    alamat_custom: Mapped[str | None] = mapped_column(String(191))
    tgl_instalasi: Mapped[date | None] = mapped_column(Date)
    blok: Mapped[str] = mapped_column(String(191), nullable=False)
    unit: Mapped[str] = mapped_column(String(191), nullable=False)
    no_telp: Mapped[str] = mapped_column(String(191), nullable=False)
    email: Mapped[str] = mapped_column(String(191), nullable=False)
    id_brand: Mapped[str | None] = mapped_column(ForeignKey('harga_layanan.id_brand'))
    layanan: Mapped[str | None] = mapped_column(String(191))
    brand_default: Mapped[str | None] = mapped_column(String(191))
    alamat_2: Mapped[str | None] = mapped_column(Text)
    
    # Relasi yang sudah ada
    data_teknis: Mapped[DataTeknis | None] = relationship(back_populates="pelanggan", uselist=False, cascade="all, delete-orphan")
    langganan: Mapped[List[Langganan]] = relationship(back_populates="pelanggan")
    harga_layanan: Mapped[HargaLayanan | None] = relationship(back_populates="pelanggan")
    
    # TAMBAHKAN RELASI INVOICES INI - Inilah yang menyebabkan error
    invoices: Mapped[List[Invoice]] = relationship(back_populates="pelanggan")