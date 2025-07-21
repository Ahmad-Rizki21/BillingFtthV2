# app/routers/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from datetime import datetime, timedelta
import asyncio

from ..database import get_db
from ..schemas.dashboard import DashboardData, StatCard, ChartData, InvoiceSummary
from ..models import Pelanggan, Langganan, Invoice, PaketLayanan, HargaLayanan, MikrotikServer
from ..services import mikrotik_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/", response_model=DashboardData)
async def get_dashboard_data(db: AsyncSession = Depends(get_db)):
    
    # --- Query untuk Stat Cards Pelanggan (Tidak Berubah) ---
    pelanggan_count_stmt = select(HargaLayanan.brand, func.count(Pelanggan.id)).join(Pelanggan, HargaLayanan.id_brand == Pelanggan.id_brand, isouter=True).group_by(HargaLayanan.brand)
    pelanggan_counts = (await db.execute(pelanggan_count_stmt)).all()
    pelanggan_by_brand = {brand.lower(): count for brand, count in pelanggan_counts}

    stat_cards = [
        StatCard(title="Jumlah Pelanggan Jakinet", value=pelanggan_by_brand.get("jakinet", 0), description="Total Pelanggan Jakinet"),
        StatCard(title="Jumlah Pelanggan Jelantik", value=pelanggan_by_brand.get("jelantik", 0), description="Total Pelanggan Jelantik"),
        StatCard(title="Pelanggan Jelantik Nagrak", value=pelanggan_by_brand.get("jelantik nagrak", 0), description="Total Pelanggan Rusun Nagrak"),
    ]

    # ==========================================================
    # --- TAMBAHAN BARU: Query untuk Stat Cards Server ---
    # ==========================================================
    
    # Ambil semua server dari DB
    all_servers = (await db.execute(select(MikrotikServer))).scalars().all()
    total_servers = len(all_servers)
    online_servers = 0

    # Cek status koneksi setiap server secara paralel
    async def check_status(server):
        api, conn = mikrotik_service.get_api_connection(server)
        if api and conn:
            conn.disconnect()
            return True
        return False

    # Jalankan semua pengecekan secara bersamaan untuk efisiensi
    results = await asyncio.gather(*(check_status(server) for server in all_servers))
    online_servers = sum(1 for res in results if res)
    offline_servers = total_servers - online_servers

    # Tambahkan hasil ke daftar stat_cards
    server_stats = [
        StatCard(title="Total Servers", value=total_servers, description="Total Mikrotik servers"),
        StatCard(title="Online Servers", value=online_servers, description="Servers currently online"),
        StatCard(title="Offline Servers", value=offline_servers, description="Servers currently offline"),
    ]
    stat_cards.extend(server_stats)
    
    # ==========================================================

    # --- Query untuk Chart (Tidak Berubah) ---
    lokasi_stmt = select(Pelanggan.alamat, func.count(Pelanggan.id)).group_by(Pelanggan.alamat).order_by(func.count(Pelanggan.id).desc()).limit(5)
    lokasi_data = (await db.execute(lokasi_stmt)).all()
    lokasi_chart = ChartData(
        labels=[item[0] for item in lokasi_data],
        data=[item[1] for item in lokasi_data]
    )

    paket_stmt = select(PaketLayanan.kecepatan, func.count(Langganan.id)).join(Langganan).group_by(PaketLayanan.kecepatan).order_by(PaketLayanan.kecepatan)
    paket_data = (await db.execute(paket_stmt)).all()
    paket_chart = ChartData(
        labels=[f"{item[0]} Mbps" for item in paket_data],
        data=[item[1] for item in paket_data]
    )

    six_months_ago = datetime.now() - timedelta(days=180)
    invoice_stmt = select(
        func.date_format(Invoice.tgl_invoice, "%Y-%m").label("bulan"),
        func.count(Invoice.id).label("total"),
        func.sum(func.if_(Invoice.status_invoice == 'Lunas', 1, 0)).label("lunas"),
        func.sum(func.if_(Invoice.status_invoice == 'Belum Dibayar', 1, 0)).label("menunggu"),
        func.sum(func.if_(Invoice.status_invoice == 'Kadaluarsa', 1, 0)).label("kadaluarsa")
    ).where(Invoice.tgl_invoice >= six_months_ago).group_by("bulan").order_by("bulan")
    
    invoice_data = (await db.execute(invoice_stmt)).all()
    
    invoice_summary_chart = InvoiceSummary(
        labels=[datetime.strptime(item[0], "%Y-%m").strftime("%b") for item in invoice_data],
        total=[item[1] if item[1] is not None else 0 for item in invoice_data],
        lunas=[item[2] if item[2] is not None else 0 for item in invoice_data],
        menunggu=[item[3] if item[3] is not None else 0 for item in invoice_data],
        kadaluarsa=[item[4] if item[4] is not None else 0 for item in invoice_data]
    )

    return DashboardData(
        stat_cards=stat_cards,
        lokasi_chart=lokasi_chart,
        paket_chart=paket_chart,
        invoice_summary_chart=invoice_summary_chart
    )