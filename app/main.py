# app/main.py
from fastapi import FastAPI
from .database import Base, engine
from .routers import pelanggan, user, role, data_teknis, harga_layanan, paket_layanan, langganan, invoice, mikrotik_server

# Fungsi untuk membuat tabel di database saat aplikasi pertama kali dijalankan
async def create_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Hati-hati, ini akan menghapus semua tabel
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="Billing System API",
    description="API untuk sistem billing terintegrasi Xendit.",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    await create_tables()

# Meng-include router pelanggan
app.include_router(pelanggan.router)
app.include_router(user.router)
app.include_router(role.router)
app.include_router(data_teknis.router)
app.include_router(harga_layanan.router)
app.include_router(langganan.router)
app.include_router(paket_layanan.router)
app.include_router(invoice.router)
app.include_router(mikrotik_server.router)

@app.get("/")
def read_root():
    return {"message": "Selamat datang di API Billing System"}
