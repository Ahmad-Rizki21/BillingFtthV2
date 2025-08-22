from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, BigInteger, func, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..database import Base

if TYPE_CHECKING:
    from .role import Role


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(191))
    email: Mapped[str] = mapped_column(
        String(191), unique=True, index=True, nullable=False
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)
    password: Mapped[str] = mapped_column(String(191), nullable=False)
    remember_token: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # AKTIFKAN KEMBALI RELASI INI - Ini adalah kunci perbaikannya
    role_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"))
    role: Mapped[Role | None] = relationship(back_populates="users")
