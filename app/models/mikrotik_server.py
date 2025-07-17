from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, BigInteger, Boolean, func, DateTime, Integer, Text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class MikrotikServer(Base):
    __tablename__ = 'mikrotik_servers'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(191), unique=True, nullable=False)
    host_ip: Mapped[str] = mapped_column(String(191), nullable=False)
    username: Mapped[str] = mapped_column(String(191), nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=8728)
    ros_version: Mapped[str | None] = mapped_column(String(191))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_connection_status: Mapped[str | None] = mapped_column(String(191))
    last_connected_at: Mapped[datetime | None] = mapped_column(TIMESTAMP)
    created_at: Mapped[datetime | None] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(server_default=func.now(), onupdate=func.now())
