# app/routers/dashboard.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from datetime import datetime, timedelta
import asyncio
from pydantic import BaseModel
from typing import Dict
from collections import defaultdict


from ..models.langganan import Langganan as LanggananModel
from ..models.invoice import Invoice as InvoiceModel

from ..database import get_db
from ..schemas.dashboard import DashboardData, StatCard, ChartData, InvoiceSummary
from ..models import Pelanggan, Langganan, Invoice, PaketLayanan, HargaLayanan, MikrotikServer
from ..services import mikrotik_service

# --- PERBAIKAN: Menambahkan prefix agar URL cocok dengan frontend ---
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# --- Skema baru untuk respons status Mikrotik ---
class MikrotikStatus(BaseModel):
    online: int
    offline: int

@router.get("/", response_model=DashboardData)
async def get_dashboard_data(db: AsyncSession = Depends(get_db)):
    # --- Query untuk Stat Cards Pelanggan ---
    pelanggan_count_stmt = select(HargaLayanan.brand, func.count(Pelanggan.id)).join(Pelanggan, HargaLayanan.id_brand == Pelanggan.id_brand, isouter=True).group_by(HargaLayanan.brand)
    pelanggan_counts = (await db.execute(pelanggan_count_stmt)).all()
    pelanggan_by_brand = {brand.lower(): count for brand, count in pelanggan_counts}

    stat_cards = [
        StatCard(title="Jumlah Pelanggan Jakinet", value=pelanggan_by_brand.get("jakinet", 0), description="Total Pelanggan Jakinet"),
        StatCard(title="Jumlah Pelanggan Jelantik", value=pelanggan_by_brand.get("jelantik", 0), description="Total Pelanggan Jelantik"),
        StatCard(title="Pelanggan Jelantik Nagrak", value=pelanggan_by_brand.get("jelantik nagrak", 0), description="Total Pelanggan Rusun Nagrak"),
    ]

    # --- Query untuk Total Server (disederhanakan) ---
    total_servers_stmt = select(func.count(MikrotikServer.id))
    total_servers = (await db.execute(total_servers_stmt)).scalar_one_or_none() or 0

    server_stats = [
        StatCard(title="Total Servers", value=total_servers, description="Total Mikrotik servers"),
        # Nilai online/offline akan diisi oleh frontend dari endpoint terpisah
        StatCard(title="Online Servers", value=0, description="Servers currently online"),
        StatCard(title="Offline Servers", value=0, description="Servers currently offline"),
    ]
    stat_cards.extend(server_stats)
    
    # --- Query untuk Chart Lokasi ---
    # NOTE: Chart ini akan terisi jika ada data di tabel Pelanggan.
    lokasi_stmt = select(Pelanggan.alamat, func.count(Pelanggan.id)).group_by(Pelanggan.alamat).order_by(func.count(Pelanggan.id).desc()).limit(5)
    lokasi_data = (await db.execute(lokasi_stmt)).all()
    lokasi_chart = ChartData(
        labels=[item[0] for item in lokasi_data if item[0] is not None],
        data=[item[1] for item in lokasi_data if item[0] is not None]
    )

    # --- Query untuk Chart Paket ---
    # NOTE: Chart ini akan terisi jika ada data di tabel PaketLayanan dan Langganan.
    paket_stmt = select(
        PaketLayanan.kecepatan, 
        func.count(Langganan.id)
    ).join(
        Langganan, 
        PaketLayanan.id == Langganan.paket_layanan_id,
        isouter=True  # LEFT JOIN untuk menampilkan semua paket
    ).group_by(
        PaketLayanan.kecepatan
    ).order_by(
        PaketLayanan.kecepatan
    )
    
    paket_data = (await db.execute(paket_stmt)).all()
    paket_chart = ChartData(
        labels=[f"{item[0]} Mbps" for item in paket_data],
        data=[item[1] for item in paket_data]
    )

    # --- Query untuk Chart Invoice ---
    # NOTE: Chart ini akan terisi jika ada data di tabel Invoice.
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
        labels=[datetime.strptime(item.bulan, "%Y-%m").strftime("%b") for item in invoice_data],
        total=[item.total or 0 for item in invoice_data],
        lunas=[item.lunas or 0 for item in invoice_data],
        menunggu=[item.menunggu or 0 for item in invoice_data],
        kadaluarsa=[item.kadaluarsa or 0 for item in invoice_data]
    )

    return DashboardData(
        stat_cards=stat_cards,
        lokasi_chart=lokasi_chart,
        paket_chart=paket_chart,
        invoice_summary_chart=invoice_summary_chart
    )


# ==========================================================
# --- ENDPOINT STATUS MIKROTIK YANG DIPERBAIKI ---
# ==========================================================
@router.get("/mikrotik-status", response_model=MikrotikStatus)
async def get_mikrotik_status(db: AsyncSession = Depends(get_db)):
    """
    Endpoint terpisah untuk memeriksa status online/offline semua server Mikrotik.
    """
    all_servers = (await db.execute(select(MikrotikServer))).scalars().all()
    total_servers = len(all_servers)
    
    if total_servers == 0:
        return MikrotikStatus(online=0, offline=0)

    # Menggunakan kembali logika yang lebih andal untuk mengecek status
    async def check_status(server):
        try:
            # Mencoba membuat koneksi adalah cara paling pasti untuk mengecek status.
            # Dijalankan di dalam executor untuk menghindari blocking.
            loop = asyncio.get_event_loop()
            api, conn = await loop.run_in_executor(
                None, mikrotik_service.get_api_connection, server
            )
            if api and conn:
                conn.disconnect()
                return True
            return False
        except Exception:
            return False

    results = await asyncio.gather(*(check_status(server) for server in all_servers))
    online_servers = sum(1 for res in results if res)
    offline_servers = total_servers - online_servers
    
    return MikrotikStatus(online=online_servers, offline=offline_servers)

# Skema untuk respons data badge
class SidebarBadgeResponse(BaseModel):
    suspended_count: int
    unpaid_invoice_count: int
    stopped_count: int

@router.get("/sidebar-badges", response_model=SidebarBadgeResponse)
async def get_sidebar_badges(db: AsyncSession = Depends(get_db)):
    """
    Endpoint untuk mengambil data angka yang akan ditampilkan sebagai badge di sidebar.
    """
    # Hitung jumlah langganan yang statusnya "Suspended"
    suspended_query = select(func.count(LanggananModel.id)).where(LanggananModel.status == "Suspended")
    suspended_result = await db.execute(suspended_query)
    suspended_count = suspended_result.scalar_one_or_none() or 0

    # Hitung jumlah invoice yang statusnya "Belum Dibayar"
    unpaid_query = select(func.count(InvoiceModel.id)).where(InvoiceModel.status_invoice == "Belum Dibayar")
    unpaid_result = await db.execute(unpaid_query)
    unpaid_count = unpaid_result.scalar_one_or_none() or 0

    stopped_query = select(func.count(LanggananModel.id)).where(LanggananModel.status == "Berhenti")
    stopped_result = await db.execute(stopped_query)
    stopped_count = stopped_result.scalar_one_or_none() or 0

    return SidebarBadgeResponse(
        suspended_count=suspended_count,
        unpaid_invoice_count=unpaid_count,
        stopped_count=stopped_count
    )
# ============================================


# =========================================== Chart untuk menampilkan penambahan User =======================================

class GrowthChartData(BaseModel):
    labels: List[str]
    data: List[int]

@router.get("/growth-trend", response_model=GrowthChartData)
async def get_growth_trend_data(db: AsyncSession = Depends(get_db)):
    """
    Menyediakan data untuk grafik tren pertumbuhan pelanggan baru per bulan.
    """
    # Query untuk menghitung jumlah pelanggan baru per bulan berdasarkan tgl_instalasi
    stmt = select(
        func.date_format(Pelanggan.tgl_instalasi, "%Y-%m").label("bulan"),
        func.count(Pelanggan.id).label("jumlah")
    ).where(
        Pelanggan.tgl_instalasi.isnot(None)
    ).group_by("bulan").order_by("bulan")
    
    result = await db.execute(stmt)
    growth_data = result.all()
    
    # Format data untuk dikirim ke frontend
    labels = [datetime.strptime(item.bulan, "%Y-%m").strftime("%b %Y") for item in growth_data]
    data = [item.jumlah for item in growth_data]
    
    return GrowthChartData(labels=labels, data=data)

# =========================================== Chart untuk menampilkan penambahan User =======================================


# --- 1. Definisikan Skema Pydantic Baru untuk Respons ---
# Ini akan mendefinisikan struktur data yang rapi untuk frontend

class BreakdownItem(BaseModel):
    """Mewakili satu item dalam rincian (misal: satu lokasi atau satu brand)."""
    nama: str
    jumlah: int

class PaketDetail(BaseModel):
    """Mewakili rincian lengkap untuk satu jenis paket."""
    total_pelanggan: int
    breakdown_lokasi: List[BreakdownItem]
    breakdown_brand: List[BreakdownItem]


# --- 2. Buat Endpoint API Baru ---

@router.get("/paket-details", response_model=Dict[str, PaketDetail])
async def get_paket_details(db: AsyncSession = Depends(get_db)):
    """
    Endpoint baru untuk memberikan rincian pelanggan per paket,
    dipecah berdasarkan lokasi dan brand.
    """
    # Query ini akan menggabungkan 4 tabel: 
    # PaketLayanan -> Langganan -> Pelanggan -> HargaLayanan (untuk brand)
    stmt = select(
        PaketLayanan.kecepatan,
        Pelanggan.alamat,
        HargaLayanan.brand,
        func.count(Pelanggan.id).label("jumlah")
    ).select_from(
        PaketLayanan
    ).join(
        Langganan, PaketLayanan.id == Langganan.paket_layanan_id
    ).join(
        Pelanggan, Langganan.pelanggan_id == Pelanggan.id
    ).join(
        HargaLayanan, Pelanggan.id_brand == HargaLayanan.id_brand
    ).group_by(
        PaketLayanan.kecepatan,
        Pelanggan.alamat,
        HargaLayanan.brand
    ).order_by(
        PaketLayanan.kecepatan,
        func.count(Pelanggan.id).desc()
    )

    result = await db.execute(stmt)
    raw_data = result.all()

    # Proses data mentah dari database menjadi struktur JSON yang kita inginkan
    paket_details = defaultdict(lambda: {
        "total_pelanggan": 0,
        "lokasi": defaultdict(int),
        "brand": defaultdict(int)
    })

    for kecepatan, alamat, brand, jumlah in raw_data:
        if not alamat or not brand: # Lewati data yang tidak lengkap
            continue
            
        paket_key = f"{kecepatan} Mbps"
        details = paket_details[paket_key]
        
        details["total_pelanggan"] += jumlah
        details["lokasi"][alamat] += jumlah
        details["brand"][brand] += jumlah

    # Format akhir agar sesuai dengan skema Pydantic
    final_response = {}
    for paket_key, details in paket_details.items():
        # Urutkan lokasi dan brand berdasarkan jumlah terbanyak
        sorted_lokasi = sorted(details["lokasi"].items(), key=lambda item: item[1], reverse=True)
        sorted_brand = sorted(details["brand"].items(), key=lambda item: item[1], reverse=True)

        final_response[paket_key] = PaketDetail(
            total_pelanggan=details["total_pelanggan"],
            breakdown_lokasi=[BreakdownItem(nama=nama, jumlah=jml) for nama, jml in sorted_lokasi],
            breakdown_brand=[BreakdownItem(nama=nama, jumlah=jml) for nama, jml in sorted_brand]
        )
        
    return final_response