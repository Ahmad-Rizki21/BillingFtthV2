# app/main.py

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from .database import Base, engine
from .routers import (
    pelanggan, user, role, data_teknis, harga_layanan, 
    paket_layanan, langganan, invoice, mikrotik_server
)
from .jobs import job_generate_invoices, job_suspend_services, job_verify_payments
from .logging_config import setup_logging

# Fungsi untuk membuat tabel di database saat aplikasi pertama kali dijalankan
async def create_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Hati-hati, ini akan menghapus semua tabel
        await conn.run_sync(Base.metadata.create_all)

# Inisialisasi aplikasi FastAPI
app = FastAPI(
    title="Billing System API",
    description="API untuk sistem billing terintegrasi Xendit.",
    version="1.0.0"
)

# Inisialisasi scheduler
scheduler = AsyncIOScheduler()

# Event handler untuk startup aplikasi
@app.on_event("startup")
async def startup_event():
    setup_logging() # <-- Panggil fungsi setup
    logger = logging.getLogger('app.main')

    # 1. Buat tabel di database
    await create_tables()
    print("Tabel telah diperiksa/dibuat.")

    # 2. Tambahkan tugas-tugas ke scheduler untuk berjalan setiap hari
    #    (Ganti 'hour' dan 'minute' sesuai kebutuhan Anda)
    
    # scheduler.add_job(job_generate_invoices, 'cron', hour=1, minute=0, timezone='Asia/Jakarta') #Real
    scheduler.add_job(job_generate_invoices, 'interval', minutes=1) 
    # scheduler.add_job(job_suspend_services, 'cron', hour=2, minute=0, timezone='Asia/Jakarta') #Real
    scheduler.add_job(job_suspend_services, 'interval', minutes=1)
    # Jalankan job verifikasi setiap jam, di menit ke-15
    # scheduler.add_job(job_verify_payments, 'cron', hour='*', minute=15, timezone='Asia/Jakarta', id="verify_payments_job") #Cek pembayaran setiap jam menit ke-15.
    scheduler.add_job(job_verify_payments, 'interval', minutes=1, id="verify_payments_job")

    
    # 3. Mulai scheduler
    scheduler.start()
    print("Scheduler telah dimulai...")

# Event handler untuk shutdown aplikasi
@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    print("Scheduler telah dimatikan.")

# Meng-include semua router
app.include_router(pelanggan.router)
app.include_router(user.router)
app.include_router(role.router)
app.include_router(data_teknis.router)
app.include_router(harga_layanan.router)
app.include_router(langganan.router)
app.include_router(paket_layanan.router)
app.include_router(invoice.router)
app.include_router(mikrotik_server.router)

# Endpoint root untuk verifikasi
@app.get("/")
def read_root():
    return {"message": "Selamat datang di API Billing System"}