from sqlalchemy import (BigInteger, ForeignKey, Date, String, func, DateTime)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base
from datetime import datetime

class Langganan(Base):
    __tablename__ = 'langganan'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    pelanggan_id: Mapped[int] = mapped_column(ForeignKey('pelanggan.id'), index=True) # Ditambahkan index untuk performa
    paket_layanan_id: Mapped[int] = mapped_column(ForeignKey('paket_layanan.id'))
    tgl_jatuh_tempo: Mapped[Date | None] = mapped_column(Date, index=True) # Ditambahkan index untuk performa
    tgl_invoice_terakhir: Mapped[Date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), default='Aktif', index=True) # Ditambahkan index untuk performa
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    pelanggan = relationship("Pelanggan", back_populates="langganan")
    paket_layanan = relationship("PaketLayanan")