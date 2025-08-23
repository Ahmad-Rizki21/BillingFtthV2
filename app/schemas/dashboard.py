# app/schemas/dashboard.py
from pydantic import BaseModel
from typing import List, Dict, Optional


class StatCard(BaseModel):
    title: str
    value: int | str
    description: str


class ChartData(BaseModel):
    labels: List[str]
    data: List[int]


class InvoiceSummary(BaseModel):
    labels: List[str]
    total: List[int]
    lunas: List[int]
    menunggu: List[int]
    kadaluarsa: List[int]


# ===== TAMBAHKAN SKEMA BARU DI SINI =====
class RevenueSummary(BaseModel):
    """Skema untuk data ringkasan pendapatan bulanan."""

    total: float
    periode: str


# ===== PERBARUI DashboardData UNTUK MENYERTAKAN PENDAPATAN =====
class DashboardData(BaseModel):
    revenue_summary: Optional[RevenueSummary] = None
    stat_cards: Optional[List[StatCard]] = None
    lokasi_chart: Optional[ChartData] = None
    paket_chart: Optional[ChartData] = None
    invoice_summary_chart: Optional[InvoiceSummary] = None
    growth_chart: Optional[ChartData] = None
