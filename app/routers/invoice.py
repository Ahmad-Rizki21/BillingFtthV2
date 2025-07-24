# app/routers/invoice.py

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from datetime import date, timedelta, datetime, timezone
from dateutil.relativedelta import relativedelta
import uuid
from typing import List, Optional
import json
import logging
import pytz
from ..websocket_manager import manager



# Impor semua model dan skema yang dibutuhkan
from ..models.invoice import Invoice as InvoiceModel
from ..models.langganan import Langganan as LanggananModel
from ..models.pelanggan import Pelanggan as PelangganModel
from ..schemas.invoice import Invoice as InvoiceSchema, InvoiceGenerate, MarkAsPaidRequest
from ..database import get_db
from ..config import settings
from ..services import xendit_service, mikrotik_service

logger = logging.getLogger('app.routers.invoice')

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
    responses={404: {"description": "Not found"}},
)




@router.get("/", response_model=List[InvoiceSchema])
async def get_all_invoices(db: AsyncSession = Depends(get_db)):
    """Mengambil semua data invoice."""
    result = await db.execute(select(InvoiceModel))
    return result.scalars().all()


def parse_xendit_datetime(iso_datetime_str: str) -> datetime:
    """Fungsi untuk mengkonversi format datetime ISO 8601 dari Xendit."""
    try:
        if not iso_datetime_str:
            return datetime.now(pytz.utc)
        if iso_datetime_str.endswith('Z'):
            iso_datetime_str = iso_datetime_str[:-1] + '+00:00'
        return datetime.fromisoformat(iso_datetime_str)
    except (ValueError, TypeError):
        return datetime.now(pytz.utc)

# Fungsi terpusat untuk memproses logika setelah pembayaran berhasil
async def _process_successful_payment(db: AsyncSession, invoice: InvoiceModel, payload: dict = None):
    """Fungsi terpusat untuk menangani logika setelah invoice lunas."""
    pelanggan = await db.get(
        PelangganModel, 
        invoice.pelanggan_id, 
        options=[selectinload(PelangganModel.langganan), selectinload(PelangganModel.data_teknis)]
    )
    if not pelanggan or not pelanggan.langganan:
        logger.error(f"Pelanggan atau langganan tidak ditemukan untuk invoice {invoice.invoice_number}")
        return

    langganan = pelanggan.langganan[0]
    old_status = langganan.status

    invoice.status_invoice = "Lunas"
    if payload:
        invoice.paid_amount = float(payload.get("paid_amount", invoice.total_harga))
        invoice.paid_at = parse_xendit_datetime(payload.get("paid_at"))
    else:
        invoice.paid_amount = invoice.total_harga
        invoice.paid_at = datetime.now(timezone.utc)

    langganan.status = "Aktif"
    current_due_date = langganan.tgl_jatuh_tempo or date.today()
    next_due_date = current_due_date + relativedelta(months=1)
    langganan.tgl_jatuh_tempo = next_due_date

    db.add(invoice)
    db.add(langganan)

    logger.info(f"Payment processed successfully for invoice {invoice.invoice_number}")

    # Kirim notifikasi ke semua admin yang terhubung
    notification_message = {
        "type": "new_payment",
        "data": {
            "invoice_number": invoice.invoice_number,
            "pelanggan_nama": pelanggan.nama,
            "total_harga": float(invoice.total_harga),
            "id_pelanggan": invoice.id_pelanggan
        }
    }
    
    await manager.broadcast(json.dumps(notification_message))

    if old_status == "Suspended":
        await mikrotik_service.trigger_mikrotik_update(db, langganan)
        logger.info(f"Mikrotik update triggered to re-activate subscription {langganan.id}")

@router.post("/xendit-callback", status_code=status.HTTP_200_OK)
async def handle_xendit_callback(request: Request, x_callback_token: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    if x_callback_token != settings.XENDIT_CALLBACK_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid callback token")

    payload = await request.json()
    logger.info(f"Xendit callback payload: {json.dumps(payload, indent=2)}")
    
    external_id = payload.get("external_id")
    xendit_status = payload.get("status")

    if not external_id:
        raise HTTPException(status_code=400, detail="External ID tidak ditemukan")

    stmt = select(InvoiceModel).where(InvoiceModel.xendit_external_id == external_id)
    invoice = (await db.execute(stmt)).scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice {external_id} tidak ditemukan")

    if invoice.status_invoice == "Lunas":
        return {"message": "Invoice already processed"}

    try:
        if xendit_status == "PAID":
            await _process_successful_payment(db, invoice, payload)
        elif xendit_status == "EXPIRED":
            invoice.status_invoice = "Kadaluarsa"
            db.add(invoice)
        
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error processing Xendit callback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing callback: {str(e)}")

    return {"message": "Callback processed successfully"}

@router.post("/generate", response_model=InvoiceSchema, status_code=status.HTTP_201_CREATED)
async def generate_manual_invoice(
    invoice_data: InvoiceGenerate,
    db: AsyncSession = Depends(get_db)
):
    """Membuat satu invoice secara manual berdasarkan langganan_id."""
    langganan = await db.get(
        LanggananModel, 
        invoice_data.langganan_id,
        options=[
            selectinload(LanggananModel.pelanggan).selectinload(PelangganModel.harga_layanan),
            selectinload(LanggananModel.pelanggan).selectinload(PelangganModel.data_teknis),
            selectinload(LanggananModel.paket_layanan)
        ]
    )
    if not langganan:
        raise HTTPException(status_code=404, detail="Langganan tidak ditemukan")

    pelanggan = langganan.pelanggan
    paket = langganan.paket_layanan
    brand = pelanggan.harga_layanan
    data_teknis = pelanggan.data_teknis

    if not all([pelanggan, paket, brand, data_teknis]):
        raise HTTPException(status_code=400, detail=f"Data pendukung tidak lengkap untuk langganan ID {langganan.id}.")

    existing_invoice_stmt = select(InvoiceModel.id).where(
        InvoiceModel.pelanggan_id == langganan.pelanggan_id,
        InvoiceModel.tgl_jatuh_tempo == langganan.tgl_jatuh_tempo
    )
    existing_invoice = (await db.execute(existing_invoice_stmt)).scalar_one_or_none()
    if existing_invoice:
        raise HTTPException(status_code=409, detail="Invoice untuk periode ini sudah ada.")

    total_harga = float(paket.harga) * (1 + (float(brand.pajak) / 100))

    jatuh_tempo_str = langganan.tgl_jatuh_tempo.strftime('%d/%m/%Y')
    deskripsi = f"Biaya berlangganan internet up to {paket.kecepatan} Mbps jatuh tempo pembayaran tanggal {jatuh_tempo_str}"
    nomor_invoice = f"INV-{pelanggan.nama.replace(' ', '')}-{langganan.tgl_jatuh_tempo.strftime('%Y%m')}-{uuid.uuid4().hex[:4].upper()}"



    new_invoice_data = {
        "invoice_number": nomor_invoice,
        "pelanggan_id": pelanggan.id,
        "id_pelanggan": data_teknis.id_pelanggan,
        "brand": brand.brand,
        "total_harga": round(total_harga, 2),
        "no_telp": pelanggan.no_telp,
        "email": pelanggan.email,
        "tgl_invoice": date.today(),
        "tgl_jatuh_tempo": langganan.tgl_jatuh_tempo,
        "status_invoice": "Belum Dibayar",
    }

    db_invoice = InvoiceModel(**new_invoice_data)
    db.add(db_invoice)
    await db.flush()

    try:
        xendit_response = await xendit_service.create_xendit_invoice(db_invoice, pelanggan, paket)
        db_invoice.payment_link = xendit_response.get("invoice_url")
        db_invoice.xendit_id = xendit_response.get("id")
        db_invoice.xendit_external_id = xendit_response.get("external_id")
        db.add(db_invoice)
        await db.commit()
        await db.refresh(db_invoice)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal membuat invoice di Xendit: {str(e)}")

    return db_invoice


@router.post("/{invoice_id}/mark-as-paid", response_model=InvoiceSchema)
async def mark_invoice_as_paid(
    invoice_id: int,
    payload: MarkAsPaidRequest,
    db: AsyncSession = Depends(get_db)
):
    """Menandai sebuah invoice sebagai lunas secara manual."""
    stmt = select(InvoiceModel).where(InvoiceModel.id == invoice_id)
    invoice = (await db.execute(stmt)).scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")

    if invoice.status_invoice == "Lunas":
        raise HTTPException(status_code=400, detail="Invoice ini sudah lunas.")

    # Set metode pembayaran dari input
    invoice.metode_pembayaran = payload.metode_pembayaran
    
    # Panggil fungsi logika pembayaran yang sudah ada
    # Kita tidak mengirim payload Xendit, jadi fungsi akan menggunakan waktu saat ini
    await _process_successful_payment(db, invoice)
    
    await db.commit()
    await db.refresh(invoice)
    
    logger.info(f"Invoice {invoice.invoice_number} ditandai lunas secara manual via {payload.metode_pembayaran}")
    
    return invoice



@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    """Menghapus satu invoice berdasarkan ID-nya."""
    
    # Cari invoice di database
    db_invoice = await db.get(InvoiceModel, invoice_id)
    
    # Jika tidak ditemukan, kirim error 404
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    
    # Jika ditemukan, hapus dari database
    await db.delete(db_invoice)
    await db.commit()
    
    return None