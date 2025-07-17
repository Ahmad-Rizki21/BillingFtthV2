# Jadikan ini baris paling pertama di file Anda
from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import date, datetime

# Impor semua tipe data yang dibutuhkan dari SQLAlchemy
from sqlalchemy import (
    BigInteger, ForeignKey, Date, String, Numeric, Text, TIMESTAMP, Boolean, func
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..database import Base

# Gunakan TYPE_CHECKING untuk menghindari circular import
if TYPE_CHECKING:
    from .pelanggan import Pelanggan

class Invoice(Base):
    __tablename__ = 'invoices'

    # Kolom Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    invoice_number: Mapped[str] = mapped_column(String(191), unique=True, nullable=False)
    
    # Foreign Key ke tabel pelanggan
    pelanggan_id: Mapped[int] = mapped_column(ForeignKey('pelanggan.id'))
    
    # Kolom denormalisasi (data yang disalin untuk kemudahan)
    id_pelanggan: Mapped[str] = mapped_column(String(255))
    brand: Mapped[str] = mapped_column(String(191))
    total_harga: Mapped[float] = mapped_column(Numeric(15, 2))
    no_telp: Mapped[str] = mapped_column(String(191))
    email: Mapped[str] = mapped_column(String(191))

    # Kolom inti invoice
    tgl_invoice: Mapped[date] = mapped_column(Date, default=date.today)
    tgl_jatuh_tempo: Mapped[date] = mapped_column(Date)
    status_invoice: Mapped[str] = mapped_column(String(50), default='Belum Dibayar')

    # Kolom untuk integrasi Xendit
    payment_link: Mapped[str | None] = mapped_column(Text)
    expiry_date: Mapped[datetime | None] = mapped_column(TIMESTAMP)
    xendit_id: Mapped[str | None] = mapped_column(String(191))
    xendit_external_id: Mapped[str | None] = mapped_column(String(191))

    # Kolom status pembayaran
    paid_amount: Mapped[float | None] = mapped_column(Numeric(15, 2))
    paid_at: Mapped[datetime | None] = mapped_column(TIMESTAMP)
    
    # Timestamps & soft delete
    is_processing: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP)

    # Definisikan relasi ke model Pelanggan
    pelanggan: Mapped["Pelanggan"] = relationship(back_populates="invoices")

