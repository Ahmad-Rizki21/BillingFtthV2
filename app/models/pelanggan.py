from sqlalchemy import (BigInteger, String, Date, Text, ForeignKey)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

class Pelanggan(Base):
    __tablename__ = 'pelanggan'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True) # Sesuai dengan PRIMARY KEY dan ix_pelanggan_id
    no_ktp: Mapped[str] = mapped_column(String(191))
    nama: Mapped[str] = mapped_column(String(191), index=True) # Sesuai dengan KEY ix_pelanggan_nama
    alamat: Mapped[str] = mapped_column(String(191))
    alamat_custom: Mapped[str | None] = mapped_column(String(191))
    alamat_2: Mapped[str | None] = mapped_column(Text)
    tgl_instalasi: Mapped[Date | None] = mapped_column(Date)
    blok: Mapped[str] = mapped_column(String(191))
    unit: Mapped[str] = mapped_column(String(191))
    no_telp: Mapped[str] = mapped_column(String(191), index=True) # Sesuai dengan KEY ix_pelanggan_no_telp
    email: Mapped[str] = mapped_column(String(191), unique=True, index=True) # Sesuai dengan KEY ix_pelanggan_email
    id_brand: Mapped[str | None] = mapped_column(ForeignKey('harga_layanan.id_brand'))
    layanan: Mapped[str | None] = mapped_column(String(191))
    brand_default: Mapped[str | None] = mapped_column(String(191))

    # Relationships
    data_teknis = relationship("DataTeknis", back_populates="pelanggan", uselist=False)
    langganan = relationship("Langganan", back_populates="pelanggan")
    invoices = relationship("Invoice", back_populates="pelanggan")
    harga_layanan = relationship("HargaLayanan", foreign_keys=[id_brand], primaryjoin="Pelanggan.id_brand == HargaLayanan.id_brand")
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
