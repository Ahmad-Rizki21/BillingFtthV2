# Jadikan ini baris paling pertama di file Anda
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import String, Integer, BigInteger, ForeignKey
from ..database import Base

if TYPE_CHECKING:
    from .pelanggan import Pelanggan

class DataTeknis(Base):
    __tablename__ = 'data_teknis'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    pelanggan_id: Mapped[int] = mapped_column(ForeignKey('pelanggan.id'))
    id_vlan: Mapped[str] = mapped_column(String(191))
    id_pelanggan: Mapped[str] = mapped_column(String(191))
    password_pppoe: Mapped[str] = mapped_column(String(191))
    ip_pelanggan: Mapped[str] = mapped_column(String(191))
    profile_pppoe: Mapped[str] = mapped_column(String(191))
    olt: Mapped[str] = mapped_column(String(191))
    olt_custom: Mapped[str | None] = mapped_column(String(191), nullable=True)
    pon: Mapped[int] = mapped_column(Integer)
    otb: Mapped[int] = mapped_column(Integer)
    odc: Mapped[int] = mapped_column(Integer)
    odp: Mapped[int] = mapped_column(Integer)
    speedtest_proof: Mapped[str | None] = mapped_column(String(191), nullable=True)
    onu_power: Mapped[int] = mapped_column(Integer)
    
    # Hapus tanda kutip dari 'Pelanggan'
    pelanggan: Mapped[Pelanggan] = relationship(back_populates="data_teknis")