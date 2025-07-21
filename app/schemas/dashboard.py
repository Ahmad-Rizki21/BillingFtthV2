# app/schemas/dashboard.py
from pydantic import BaseModel
from typing import List, Dict

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

class DashboardData(BaseModel):
    stat_cards: List[StatCard]
    lokasi_chart: ChartData
    paket_chart: ChartData
    invoice_summary_chart: InvoiceSummary