# Jadikan ini baris paling pertama di file Anda
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import String, Integer, BigInteger, ForeignKey
from ..database import Base

if TYPE_CHECKING:
    from .pelanggan import Pelanggan
    from .mikrotik_server import MikrotikServer

class DataTeknis(Base):
    __tablename__ = 'data_teknis'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    pelanggan_id: Mapped[int] = mapped_column(ForeignKey('pelanggan.id'), index=True)
    id_vlan: Mapped[str] = mapped_column(String(191))
    id_pelanggan: Mapped[str] = mapped_column(String(191), index=True)
    password_pppoe: Mapped[str] = mapped_column(String(191))
    ip_pelanggan: Mapped[str] = mapped_column(String(191), index=True)
    profile_pppoe: Mapped[str] = mapped_column(String(191))
    olt: Mapped[str] = mapped_column(String(191), index=True)
    olt_custom: Mapped[str | None] = mapped_column(String(191), nullable=True)
    pon: Mapped[int | None] = mapped_column(Integer, nullable=True)
    otb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    odc: Mapped[int | None] = mapped_column(Integer, nullable=True)
    odp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    onu_power: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sn: Mapped[str | None] = mapped_column(String(191), nullable=True, index=True)
    speedtest_proof: Mapped[str | None] = mapped_column(String(191), nullable=True)

    mikrotik_server_id: Mapped[int | None] = mapped_column(ForeignKey('mikrotik_servers.id'))
    mikrotik_server: Mapped["MikrotikServer"] = relationship(back_populates="data_teknis_pelanggan")
    
    # Hapus tanda kutip dari 'Pelanggan'
    pelanggan: Mapped[Pelanggan] = relationship(back_populates="data_teknis")